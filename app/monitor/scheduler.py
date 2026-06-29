"""APScheduler 기반 모니터링 자동 실행."""

from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models.orm import MonitorProject, MonitorQuestion, MonitorRun
from app.monitor.ai_clients import ALL_CALLERS

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def run_project(project_id: int) -> int:
    """프로젝트의 활성 질문 전체를 AI 모델에 실행하고 결과를 저장. 실행 건수 반환."""
    if AsyncSessionLocal is None:
        return 0

    async with AsyncSessionLocal() as db:
        project = await db.get(MonitorProject, project_id)
        if not project:
            return 0

        q_result = await db.execute(
            select(MonitorQuestion).where(
                MonitorQuestion.project_id == project_id,
                MonitorQuestion.active == True,
            )
        )
        questions = q_result.scalars().all()
        if not questions:
            return 0

        brand = project.brand_keyword
        count = 0

        async def _call(question: MonitorQuestion, caller_fn, model_name: str) -> None:
            nonlocal count
            try:
                from app.monitor.ai_clients import AiResponse
                resp: AiResponse = await caller_fn(question.question, brand)
                run = MonitorRun(
                    question_id=question.id,
                    ai_model=model_name,
                    mentioned=resp.mentioned,
                    response_snippet=resp.snippet,
                    rank=resp.rank,
                )
                db.add(run)
                count += 1
            except Exception as e:
                logger.warning("모니터링 실행 실패 project=%d model=%s: %s", project_id, model_name, e)

        tasks = [
            _call(q, caller_fn, model_name)
            for q in questions
            for model_name, caller_fn, has_key in ALL_CALLERS
            if has_key()
        ]
        await asyncio.gather(*tasks)
        await db.commit()

    logger.info("프로젝트 %d 모니터링 완료: %d건", project_id, count)
    return count


async def run_all_projects() -> None:
    """모든 프로젝트를 순차 실행 (스케줄러 진입점)."""
    if AsyncSessionLocal is None:
        logger.warning("DATABASE_URL 미설정 — 스케줄 실행 건너뜀")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MonitorProject.id))
        project_ids = result.scalars().all()

    logger.info("스케줄 실행 시작: %d개 프로젝트", len(project_ids))
    for pid in project_ids:
        await run_project(pid)
    logger.info("스케줄 실행 완료")


def start_scheduler() -> None:
    """FastAPI startup에서 호출."""
    # 매일 오전 9시 (KST) 자동 실행
    scheduler.add_job(
        run_all_projects,
        CronTrigger(hour=9, minute=0),
        id="daily_monitor",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("모니터링 스케줄러 시작 — 매일 09:00 KST 자동 실행")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
