"""Monitor 모듈 FastAPI 라우터."""

from __future__ import annotations

from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.orm import MonitorMention, MonitorProject, MonitorQuestion, MonitorRun
from app.monitor.ai_clients import ENGINES
from app.monitor.extraction import matches_brand
from app.monitor.runner import RunSummary, execute_project

router = APIRouter(prefix="/monitor", tags=["monitor"])


# ── Pydantic 스키마 ────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    target_url: str
    mode: str = "brand"          # local | brand
    brand_keyword: str           # 언급 감지용 키워드 (예: "이루다치과")
    owner_email: str | None = None


class ProjectOut(BaseModel):
    id: int
    name: str
    target_url: str
    mode: str
    brand_keyword: str
    created_at: datetime

    model_config = {"from_attributes": True}


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


# ── 엔드포인트 ────────────────────────────────────────────────

@router.post("/projects", response_model=ProjectOut, status_code=201)
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


@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(MonitorProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@router.post("/projects/{project_id}/questions", response_model=QuestionOut, status_code=201)
async def add_question(project_id: int, body: QuestionCreate, db: AsyncSession = Depends(get_db)):
    project = await db.get(MonitorProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    q = MonitorQuestion(project_id=project_id, question=body.question)
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


@router.get("/projects/{project_id}/questions", response_model=list[QuestionOut])
async def list_questions(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MonitorQuestion)
        .where(MonitorQuestion.project_id == project_id, MonitorQuestion.active == True)
    )
    return result.scalars().all()


@router.delete("/projects/{project_id}/questions/{question_id}", status_code=204)
async def deactivate_question(project_id: int, question_id: int, db: AsyncSession = Depends(get_db)):
    """질문을 목록에서 내린다.

    행을 지우지 않고 active=False로 둔다. 이미 실행된 이력(run/mention)은
    비용을 들여 얻은 데이터라 질문 하나 지운다고 함께 버릴 이유가 없다.
    """
    question = await db.get(MonitorQuestion, question_id)
    if not question or question.project_id != project_id:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
    question.active = False
    await db.commit()


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """프로젝트와 딸린 질문·실행이력·언급을 모두 삭제한다."""
    project = await db.get(MonitorProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    # ORM 캐스케이드는 관계를 적재해야 동작해 async에서 지연로딩 오류가 난다.
    # 자식부터 순서대로 명시 삭제한다.
    question_ids = select(MonitorQuestion.id).where(MonitorQuestion.project_id == project_id)
    run_ids = select(MonitorRun.id).where(MonitorRun.question_id.in_(question_ids))

    await db.execute(delete(MonitorMention).where(MonitorMention.run_id.in_(run_ids)))
    await db.execute(delete(MonitorRun).where(MonitorRun.question_id.in_(question_ids)))
    await db.execute(delete(MonitorQuestion).where(MonitorQuestion.project_id == project_id))
    await db.execute(delete(MonitorProject).where(MonitorProject.id == project_id))
    await db.commit()


@router.post("/projects/{project_id}/run", response_model=list[RunSummary])
async def run_monitor(project_id: int, db: AsyncSession = Depends(get_db)):
    """활성 질문 전체를 가용 AI 모델에 병렬 실행하고 결과를 DB에 저장."""
    project = await db.get(MonitorProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    summaries = await execute_project(db, project)
    if not summaries:
        raise HTTPException(
            status_code=400,
            detail="활성 질문이 없거나 사용 가능한 AI 엔진이 없습니다.",
        )
    return summaries


@router.get("/projects/{project_id}/dashboard", response_model=Dashboard)
async def get_dashboard(project_id: int, db: AsyncSession = Depends(get_db)):
    """질문별·AI모델별 전체 언급률 집계."""
    project = await db.get(MonitorProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    q_result = await db.execute(
        select(MonitorQuestion)
        .where(MonitorQuestion.project_id == project_id, MonitorQuestion.active == True)
    )
    questions = q_result.scalars().all()

    # 프로젝트 전체 run을 한 번에 조회 (질문별 N+1 방지)
    run_result = await db.execute(
        select(MonitorRun)
        .join(MonitorQuestion, MonitorRun.question_id == MonitorQuestion.id)
        .where(MonitorQuestion.project_id == project_id)
        .order_by(MonitorRun.ran_at.desc())
    )
    all_runs = run_result.scalars().all()

    runs_by_question: dict[int, list[MonitorRun]] = {}
    for r in all_runs:
        runs_by_question.setdefault(r.question_id, []).append(r)

    # 추천된 업체(내 브랜드 + 경쟁사)도 한 번에 조회
    mention_result = await db.execute(
        select(MonitorMention, MonitorRun.question_id)
        .join(MonitorRun, MonitorMention.run_id == MonitorRun.id)
        .join(MonitorQuestion, MonitorRun.question_id == MonitorQuestion.id)
        .where(MonitorQuestion.project_id == project_id)
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
        project_id=project_id,
        project_name=project.name,
        total_mention_rate=total_rate,
        rows=rows,
        by_model=by_model,
        share_of_voice=_aggregate_brands(all_mentions, project.brand_keyword),
    )
