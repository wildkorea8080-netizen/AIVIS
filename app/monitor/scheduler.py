"""APScheduler 기반 모니터링 자동 실행."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models.orm import MonitorProject
from app.monitor.runner import execute_project

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def run_project(project_id: int) -> int:
    """프로젝트의 활성 질문 전체를 AI 모델에 실행하고 결과를 저장. 성공 건수 반환."""
    if AsyncSessionLocal is None:
        return 0

    async with AsyncSessionLocal() as db:
        project = await db.get(MonitorProject, project_id)
        if not project:
            return 0
        summaries = await execute_project(db, project)

    count = sum(1 for s in summaries for r in s.results if r.error is None)
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
