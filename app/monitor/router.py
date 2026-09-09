"""Monitor 모듈 FastAPI 라우터.

접근 방식이 두 가지 공존한다:
  - /monitor/projects/{id}  : 정수 id. 열거가 가능해 폐기 예정이며, 프론트 전환이
                              끝나면 제거한다. 소유 토큰은 절대 반환하지 않는다.
  - /monitor/p/{token}      : capability URL. 앞으로의 정식 경로.
라우팅만 다르고 실제 동작은 아래 공용 함수 한 벌을 공유한다.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.orm import MonitorMention, MonitorProject, MonitorQuestion, MonitorRun
from app.monitor.ai_clients import ENGINES
from app.monitor.extraction import matches_brand
from app.monitor.runner import RunSummary, execute_project

router = APIRouter(prefix="/monitor", tags=["monitor"])

# 링크를 가진 누구나 실행을 반복하면 소유자에게 API 비용이 청구된다.
RUN_COOLDOWN = timedelta(minutes=10)

# 배치 조회 1회에 허용할 토큰 수
MAX_BATCH_TOKENS = 20


# ── Pydantic 스키마 ────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    target_url: str
    mode: str = "brand"          # local | brand
    brand_keyword: str           # 언급 감지용 키워드 (예: "이루다치과")
    owner_email: str | None = None


class ProjectOut(BaseModel):
    """정수 id 경로용. owner_token을 포함하지 않는다 —
    id를 훑어 토큰을 수집할 수 있으면 토큰을 쓰는 의미가 없다."""

    id: int
    name: str
    target_url: str
    mode: str
    brand_keyword: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectOwnerOut(ProjectOut):
    """토큰을 이미 가진 쪽에만 돌려준다(생성 응답, 토큰 경로)."""

    owner_token: str


class ProjectSummary(BaseModel):
    """목록 화면용 요약."""

    owner_token: str
    name: str
    target_url: str
    mode: str
    brand_keyword: str
    created_at: datetime
    question_count: int
    last_run_at: datetime | None


class BatchLookup(BaseModel):
    tokens: list[str] = Field(default_factory=list)


class QuestionCreate(BaseModel):
    question: str


class QuestionOut(BaseModel):
    id: int
    question: str
    active: bool

    model_config = {"from_attributes": True}


class BrandStat(BaseModel):
    name: str                # 대표 표기 (가장 자주 쓰인 name_raw)
    name_key: str
    mentions: int            # 추천된 횟수
    avg_rank: float | None   # 평균 추천 순위
    is_own: bool             # 내 브랜드인지


class DashboardRow(BaseModel):
    question_id: int
    question: str
    runs: list[dict]             # [{ai_model, mentioned, ran_at}, ...]
    mention_rate: float          # 전체 언급률 (0.0~1.0)
    competitors: list[BrandStat] = []   # 이 질문에서 AI가 추천한 업체들


class ModelStat(BaseModel):
    ai_model: str
    label: str
    configured: bool         # API 키 설정 여부 — false면 "미설정"이지 "0% 언급"이 아님
    total_runs: int
    mentioned_runs: int
    rate: float              # 언급률 (0.0~1.0)
    avg_rank: float | None   # 언급됐을 때 평균 추천 순위


class Dashboard(BaseModel):
    project_id: int
    project_name: str
    total_mention_rate: float
    rows: list[DashboardRow]
    by_model: list[ModelStat]
    share_of_voice: list[BrandStat] = []   # 프로젝트 전체 점유율


# ── 조회 헬퍼 ──────────────────────────────────────────────────

_NOT_FOUND = "프로젝트를 찾을 수 없습니다."


async def _by_id(db: AsyncSession, project_id: int) -> MonitorProject:
    project = await db.get(MonitorProject, project_id)
    if not project or project.deleted_at is not None:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)
    return project


async def _by_token(db: AsyncSession, token: str) -> MonitorProject:
    result = await db.execute(
        select(MonitorProject).where(
            MonitorProject.owner_token == token,
            MonitorProject.deleted_at.is_(None),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)
    return project


# ── 공용 로직 (라우팅과 무관) ──────────────────────────────────

def _aggregate_brands(mentions: list[MonitorMention], brand_keyword: str) -> list[BrandStat]:
    """name_key로 묶어 언급 수 내림차순으로 정렬한다."""
    groups: dict[str, list[MonitorMention]] = {}
    for m in mentions:
        groups.setdefault(m.name_key, []).append(m)

    stats: list[BrandStat] = []
    for key, items in groups.items():
        # 같은 업체라도 AI마다 표기가 흔들리므로 가장 자주 쓰인 원문을 대표로 삼는다
        ranks = [i.rank for i in items]
        stats.append(BrandStat(
            name=Counter(i.name_raw for i in items).most_common(1)[0][0],
            name_key=key,
            mentions=len(items),
            avg_rank=round(sum(ranks) / len(ranks), 1) if ranks else None,
            is_own=matches_brand(key, brand_keyword),
        ))

    stats.sort(key=lambda s: (-s.mentions, s.avg_rank if s.avg_rank is not None else 99.0))
    return stats


async def _active_questions(db: AsyncSession, project: MonitorProject) -> list[MonitorQuestion]:
    result = await db.execute(
        select(MonitorQuestion).where(
            MonitorQuestion.project_id == project.id,
            MonitorQuestion.active.is_(True),
        )
    )
    return list(result.scalars().all())


async def _create_question(db: AsyncSession, project: MonitorProject, text: str) -> MonitorQuestion:
    question = MonitorQuestion(project_id=project.id, question=text)
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def _retire_question(db: AsyncSession, project: MonitorProject, question_id: int) -> None:
    """질문을 목록에서 내린다.

    행을 지우지 않고 active=False로 둔다. 이미 실행된 이력(run/mention)은
    비용을 들여 얻은 데이터라 질문 하나 내린다고 함께 버릴 이유가 없다.
    """
    question = await db.get(MonitorQuestion, question_id)
    if not question or question.project_id != project.id:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
    question.active = False
    await db.commit()


async def _retire_project(db: AsyncSession, project: MonitorProject) -> None:
    """프로젝트를 목록에서 내린다(소프트 삭제).

    대시보드 주소를 아는 사람이면 누구나 호출할 수 있으므로 행을 지우지 않는다.
    실행 이력은 API 비용을 들여 얻은 데이터라 되돌릴 수 없게 파괴되면 안 된다.
    """
    project.deleted_at = datetime.now(timezone.utc)
    await db.commit()


def cooldown_remaining(last_run_at: datetime | None, now: datetime) -> timedelta | None:
    """남은 쿨다운 시간. None이면 지금 실행해도 된다."""
    if last_run_at is None:
        return None
    elapsed = now - last_run_at
    if elapsed >= RUN_COOLDOWN:
        return None
    return RUN_COOLDOWN - elapsed


async def _last_run_at(db: AsyncSession, project: MonitorProject) -> datetime | None:
    result = await db.execute(
        select(func.max(MonitorRun.ran_at))
        .join(MonitorQuestion, MonitorRun.question_id == MonitorQuestion.id)
        .where(MonitorQuestion.project_id == project.id)
    )
    return result.scalar_one_or_none()


async def _run(db: AsyncSession, project: MonitorProject) -> list[RunSummary]:
    remaining = cooldown_remaining(
        await _last_run_at(db, project), datetime.now(timezone.utc)
    )
    if remaining is not None:
        wait = int(remaining.total_seconds() // 60) + 1
        raise HTTPException(
            status_code=429,
            detail=f"방금 실행했습니다. {wait}분 후에 다시 시도해주세요.",
        )

    summaries = await execute_project(db, project)
    if not summaries:
        raise HTTPException(
            status_code=400,
            detail="활성 질문이 없거나 사용 가능한 AI 엔진이 없습니다.",
        )
    return summaries


async def _dashboard(db: AsyncSession, project: MonitorProject) -> Dashboard:
    questions = await _active_questions(db, project)

    # 프로젝트 전체 run을 한 번에 조회 (질문별 N+1 방지)
    run_result = await db.execute(
        select(MonitorRun)
        .join(MonitorQuestion, MonitorRun.question_id == MonitorQuestion.id)
        .where(MonitorQuestion.project_id == project.id)
        .order_by(MonitorRun.ran_at.desc())
    )
    all_runs = list(run_result.scalars().all())

    runs_by_question: dict[int, list[MonitorRun]] = {}
    for r in all_runs:
        runs_by_question.setdefault(r.question_id, []).append(r)

    # 추천된 업체(내 브랜드 + 경쟁사)도 한 번에 조회
    mention_result = await db.execute(
        select(MonitorMention, MonitorRun.question_id)
        .join(MonitorRun, MonitorMention.run_id == MonitorRun.id)
        .join(MonitorQuestion, MonitorRun.question_id == MonitorQuestion.id)
        .where(MonitorQuestion.project_id == project.id)
    )
    mention_rows = mention_result.all()
    all_mentions = [m for m, _ in mention_rows]

    mentions_by_question: dict[int, list[MonitorMention]] = {}
    for m, qid in mention_rows:
        mentions_by_question.setdefault(qid, []).append(m)

    rows: list[DashboardRow] = []
    for q in questions:
        runs = runs_by_question.get(q.id, [])
        mentioned_count = sum(1 for r in runs if r.mentioned)
        rows.append(DashboardRow(
            question_id=q.id,
            question=q.question,
            runs=[
                {
                    "ai_model": r.ai_model,
                    "mentioned": r.mentioned,
                    "rank": r.rank,
                    "ran_at": r.ran_at.isoformat(),
                }
                for r in runs
            ],
            mention_rate=mentioned_count / len(runs) if runs else 0.0,
            competitors=_aggregate_brands(
                mentions_by_question.get(q.id, []), project.brand_keyword
            ),
        ))

    total_rate = sum(1 for r in all_runs if r.mentioned) / len(all_runs) if all_runs else 0.0

    # 엔진별 집계 — 등록된 모든 엔진을 반환해 차트 축을 고정한다
    by_model: list[ModelStat] = []
    for engine in ENGINES:
        engine_runs = [r for r in all_runs if r.ai_model == engine.name]
        mentioned = [r for r in engine_runs if r.mentioned]
        ranks = [r.rank for r in mentioned if r.rank is not None]
        by_model.append(ModelStat(
            ai_model=engine.name,
            label=engine.label,
            configured=engine.has_key(),
            total_runs=len(engine_runs),
            mentioned_runs=len(mentioned),
            rate=len(mentioned) / len(engine_runs) if engine_runs else 0.0,
            avg_rank=round(sum(ranks) / len(ranks), 1) if ranks else None,
        ))

    return Dashboard(
        project_id=project.id,
        project_name=project.name,
        total_mention_rate=total_rate,
        rows=rows,
        by_model=by_model,
        share_of_voice=_aggregate_brands(all_mentions, project.brand_keyword),
    )


# ── 생성 · 배치 조회 ───────────────────────────────────────────

@router.post("/projects", response_model=ProjectOwnerOut, status_code=201)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = MonitorProject(
        name=body.name,
        target_url=body.target_url,
        mode=body.mode,
        brand_keyword=body.brand_keyword,
        owner_email=body.owner_email,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.post("/projects/batch", response_model=list[ProjectSummary])
async def lookup_projects(body: BatchLookup, db: AsyncSession = Depends(get_db)):
    """토큰 여러 개를 한 번에 조회한다(목록 화면용).

    GET이 아니라 POST인 이유는 토큰이 URL·접근 로그에 남지 않게 하기 위함이다.
    모르는 토큰은 조용히 빼고 돌려준다 — 하나 때문에 전체를 404로 만들면
    호출부가 삭제된 항목을 스스로 정리할 수 없다.
    """
    tokens = body.tokens[:MAX_BATCH_TOKENS]
    if not tokens:
        return []

    result = await db.execute(
        select(MonitorProject).where(
            MonitorProject.owner_token.in_(tokens),
            MonitorProject.deleted_at.is_(None),
        )
    )
    projects = list(result.scalars().all())
    if not projects:
        return []

    project_ids = [p.id for p in projects]

    counts = dict((await db.execute(
        select(MonitorQuestion.project_id, func.count(MonitorQuestion.id))
        .where(
            MonitorQuestion.project_id.in_(project_ids),
            MonitorQuestion.active.is_(True),
        )
        .group_by(MonitorQuestion.project_id)
    )).all())

    last_runs = dict((await db.execute(
        select(MonitorQuestion.project_id, func.max(MonitorRun.ran_at))
        .join(MonitorRun, MonitorRun.question_id == MonitorQuestion.id)
        .where(MonitorQuestion.project_id.in_(project_ids))
        .group_by(MonitorQuestion.project_id)
    )).all())

    summaries = [
        ProjectSummary(
            owner_token=p.owner_token,
            name=p.name,
            target_url=p.target_url,
            mode=p.mode,
            brand_keyword=p.brand_keyword,
            created_at=p.created_at,
            question_count=counts.get(p.id, 0),
            last_run_at=last_runs.get(p.id),
        )
        for p in projects
    ]
    # 요청한 토큰 순서를 유지해 호출부가 정렬을 다시 하지 않아도 되게 한다
    order = {t: i for i, t in enumerate(tokens)}
    summaries.sort(key=lambda s: order[s.owner_token])
    return summaries


# ── 토큰 경로 (정식) ───────────────────────────────────────────

@router.get("/p/{token}", response_model=ProjectOwnerOut)
async def get_project_by_token(token: str, db: AsyncSession = Depends(get_db)):
    return await _by_token(db, token)


@router.get("/p/{token}/questions", response_model=list[QuestionOut])
async def list_questions_by_token(token: str, db: AsyncSession = Depends(get_db)):
    return await _active_questions(db, await _by_token(db, token))


@router.post("/p/{token}/questions", response_model=QuestionOut, status_code=201)
async def add_question_by_token(token: str, body: QuestionCreate, db: AsyncSession = Depends(get_db)):
    return await _create_question(db, await _by_token(db, token), body.question)


@router.delete("/p/{token}/questions/{question_id}", status_code=204)
async def retire_question_by_token(token: str, question_id: int, db: AsyncSession = Depends(get_db)):
    await _retire_question(db, await _by_token(db, token), question_id)


@router.delete("/p/{token}", status_code=204)
async def retire_project_by_token(token: str, db: AsyncSession = Depends(get_db)):
    await _retire_project(db, await _by_token(db, token))


@router.post("/p/{token}/run", response_model=list[RunSummary])
async def run_by_token(token: str, db: AsyncSession = Depends(get_db)):
    return await _run(db, await _by_token(db, token))


@router.get("/p/{token}/dashboard", response_model=Dashboard)
async def dashboard_by_token(token: str, db: AsyncSession = Depends(get_db)):
    return await _dashboard(db, await _by_token(db, token))


# ── 정수 id 경로 (폐기 예정) ───────────────────────────────────
# 프론트가 토큰 경로로 넘어가면 이 블록을 통째로 삭제한다.
# 그때까지는 구 버전 프론트가 계속 동작하도록 남겨둔다.

@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    return await _by_id(db, project_id)


@router.get("/projects/{project_id}/questions", response_model=list[QuestionOut])
async def list_questions(project_id: int, db: AsyncSession = Depends(get_db)):
    return await _active_questions(db, await _by_id(db, project_id))


@router.post("/projects/{project_id}/questions", response_model=QuestionOut, status_code=201)
async def add_question(project_id: int, body: QuestionCreate, db: AsyncSession = Depends(get_db)):
    return await _create_question(db, await _by_id(db, project_id), body.question)


@router.delete("/projects/{project_id}/questions/{question_id}", status_code=204)
async def deactivate_question(project_id: int, question_id: int, db: AsyncSession = Depends(get_db)):
    await _retire_question(db, await _by_id(db, project_id), question_id)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    await _retire_project(db, await _by_id(db, project_id))


@router.post("/projects/{project_id}/run", response_model=list[RunSummary])
async def run_monitor(project_id: int, db: AsyncSession = Depends(get_db)):
    return await _run(db, await _by_id(db, project_id))


@router.get("/projects/{project_id}/dashboard", response_model=Dashboard)
async def get_dashboard(project_id: int, db: AsyncSession = Depends(get_db)):
    return await _dashboard(db, await _by_id(db, project_id))
