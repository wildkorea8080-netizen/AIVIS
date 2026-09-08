"""모니터링 실행 공용 로직.

router(수동 실행)와 scheduler(자동 실행)가 같은 경로를 쓰도록 여기 한 곳에 둔다.
"""

from __future__ import annotations

import asyncio
import logging

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import MonitorProject, MonitorQuestion, MonitorRun
from app.monitor.ai_clients import ENGINES, AiResponse

logger = logging.getLogger(__name__)


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


async def execute_project(db: AsyncSession, project: MonitorProject) -> list[RunSummary]:
    """활성 질문 × 가용 엔진을 병렬 실행하고 결과를 저장한다.

    질문이 없거나 키가 등록된 엔진이 없으면 빈 리스트를 반환한다.
    개별 호출 실패는 RunResult.error로 흡수되어 나머지 실행을 막지 않는다.
    """
    result = await db.execute(
        select(MonitorQuestion).where(
            MonitorQuestion.project_id == project.id,
            MonitorQuestion.active == True,  # noqa: E712 — SQL 표현식
        )
    )
    questions = result.scalars().all()
    if not questions:
        return []

    brand = project.brand_keyword

    async def _call(question: MonitorQuestion, engine_name: str, caller) -> RunResult:
        try:
            resp: AiResponse = await caller(question.question, brand)
        except Exception as e:
            logger.warning(
                "모니터링 호출 실패 project=%d question=%d model=%s: %s",
                project.id, question.id, engine_name, e,
            )
            return RunResult(ai_model=engine_name, mentioned=False, rank=None, snippet=None, error=str(e))

        db.add(MonitorRun(
            question_id=question.id,
            ai_model=engine_name,
            mentioned=resp.mentioned,
            response_snippet=resp.snippet,
            rank=resp.rank,
        ))
        return RunResult(
            ai_model=engine_name,
            mentioned=resp.mentioned,
            rank=resp.rank,
            snippet=resp.snippet,
        )

    tasks = []
    task_questions: list[MonitorQuestion] = []
    for q in questions:
        for engine in ENGINES:
            if not engine.has_key():
                continue
            tasks.append(_call(q, engine.name, engine.call))
            task_questions.append(q)

    if not tasks:
        logger.warning("가용 AI 엔진 없음 — project=%d 실행 건너뜀", project.id)
        return []

    run_results = await asyncio.gather(*tasks)
    await db.commit()

    summaries: dict[int, RunSummary] = {}
    for question, run_result in zip(task_questions, run_results):
        summary = summaries.get(question.id)
        if summary is None:
            summary = RunSummary(question_id=question.id, question=question.question, results=[])
            summaries[question.id] = summary
        summary.results.append(run_result)

    return list(summaries.values())
