"""Monitor 모듈 FastAPI 라우터."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.orm import MonitorProject, MonitorQuestion, MonitorRun
from app.monitor.ai_clients import ENGINES, AiResponse

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


class RunResult(BaseModel):
    ai_model: str
    mentioned: bool
    rank: int | None
    snippet: str | None
    error: str | None = None


class RunSummary(BaseModel):
    question_id: int
    question: str
    results: list[RunResult]


class DashboardRow(BaseModel):
    question_id: int
    question: str
    runs: list[dict]             # [{ai_model, mentioned, ran_at}, ...]
    mention_rate: float          # 전체 언급률 (0.0~1.0)


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


@router.post("/projects/{project_id}/run", response_model=list[RunSummary])
async def run_monitor(project_id: int, db: AsyncSession = Depends(get_db)):
    """활성 질문 전체를 가용 AI 모델에 병렬 실행하고 결과를 DB에 저장."""
    project = await db.get(MonitorProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    result = await db.execute(
        select(MonitorQuestion)
        .where(MonitorQuestion.project_id == project_id, MonitorQuestion.active == True)
    )
    questions = result.scalars().all()
    if not questions:
        raise HTTPException(status_code=400, detail="활성 질문이 없습니다.")

    brand = project.brand_keyword
    summaries: list[RunSummary] = []

    async def _call_one(q: MonitorQuestion, caller_fn, model_name: str) -> RunResult:
        try:
            resp: AiResponse = await caller_fn(q.question, brand)
            run = MonitorRun(
                question_id=q.id,
                ai_model=model_name,
                mentioned=resp.mentioned,
                response_snippet=resp.snippet,
                rank=resp.rank,
            )
            db.add(run)
            return RunResult(
                ai_model=model_name,
                mentioned=resp.mentioned,
                rank=resp.rank,
                snippet=resp.snippet,
            )
        except Exception as e:
            return RunResult(ai_model=model_name, mentioned=False, rank=None, snippet=None, error=str(e))

    # 질문 × AI모델 전체 병렬 실행
    tasks = []
    task_meta = []
    for q in questions:
        for engine in ENGINES:
            if not engine.has_key():
                continue
            tasks.append(_call_one(q, engine.call, engine.name))
            task_meta.append((q.id, q.question))

    raw_results = await asyncio.gather(*tasks)
    await db.commit()

    # 질문별로 묶기
    question_map: dict[int, RunSummary] = {}
    for (qid, qtxt), run_result in zip(task_meta, raw_results):
        if qid not in question_map:
            question_map[qid] = RunSummary(question_id=qid, question=qtxt, results=[])
        question_map[qid].results.append(run_result)

    return list(question_map.values())


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
    )
