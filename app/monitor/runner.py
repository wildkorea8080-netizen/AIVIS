"""모니터링 실행 공용 로직.

router(수동 실행)와 scheduler(자동 실행)가 같은 경로를 쓰도록 여기 한 곳에 둔다.
"""

from __future__ import annotations

import asyncio
import logging

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import MonitorMention, MonitorProject, MonitorQuestion, MonitorRun
from app.monitor.ai_clients import ENGINES, AiResponse

logger = logging.getLogger(__name__)


class RunResult(BaseModel):
    ai_model: str
    mentioned: bool
    rank: int | None
    snippet: str | None
    competitors: list[str] = []   # 이 응답에서 추천된 업체 (순서대로, 내 브랜드 포함)
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

        run = MonitorRun(
            question_id=question.id,
            ai_model=engine_name,
            mentioned=resp.mentioned,
            response_snippet=resp.snippet,
            response_text=resp.text,
            rank=resp.rank,
        )
        # 관계로 붙이면 flush 시 run_id가 자동으로 채워진다.
        # 동시 실행 중이라 여기서 await db.flush()를 부르면 세션이 깨진다.
        run.mentions = [
            MonitorMention(name_raw=m.name_raw, name_key=m.name_key, rank=m.rank)
            for m in resp.mentions
        ]
        db.add(run)

        if not resp.mentions:
            logger.info(
                "추천 목록 파싱 0건 project=%d model=%s — 응답이 번호 목록 형식이 아닐 수 있음",
                project.id, engine_name,
            )

        return RunResult(
            ai_model=engine_name,
            mentioned=resp.mentioned,
            rank=resp.rank,
            snippet=resp.snippet,
            competitors=[m.name_raw for m in resp.mentions],
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
