from __future__ import annotations

import asyncio

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import AuditContext, BaseCollector
from app.collectors.llmstxt_collector import LlmsTxtCollector
from app.collectors.mention_collector import MentionCollector
from app.collectors.place_collector import PlaceCollector
from app.collectors.robots_collector import RobotsCollector
from app.collectors.schema_collector import SchemaCollector
from app.config import settings
from app.db import get_db
from app.models.orm import AuditReport
from app.models.schemas import AuditRequest, Finding, ReadinessReport, SignalResult
from app.scoring.engine import compute_score
from app.monitor.router import router as monitor_router

app = FastAPI(title="AIVIS", description="AEO/GEO AI 검색 노출 진단 API", version="0.1.0")
app.include_router(monitor_router)

_COLLECTORS: list[BaseCollector] = [
    SchemaCollector(),
    LlmsTxtCollector(),
    RobotsCollector(),
    PlaceCollector(),
    MentionCollector(),
]


async def _safe_collect(collector: BaseCollector, ctx: AuditContext) -> SignalResult:
    try:
        return await collector.collect(ctx)
    except Exception as e:
        return SignalResult(
            collector=type(collector).__name__,
            status="error",
            findings=[],
            error=f"Unhandled: {e}",
        )


@app.post("/audit", response_model=ReadinessReport)
async def audit(req: AuditRequest, db: AsyncSession = Depends(get_db)) -> ReadinessReport:
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        ctx = AuditContext.from_url(
            url=str(req.url),
            place_name=req.place_name,
            region=req.region,
            mode=req.mode,
            client=client,
        )
        results: list[SignalResult] = list(
            await asyncio.gather(*[_safe_collect(c, ctx) for c in _COLLECTORS])
        )

    all_findings: list[Finding] = [f for r in results for f in r.findings]
    score = compute_score(req.mode, all_findings)

    report = ReadinessReport(
        target_url=str(req.url),
        place_name=req.place_name,
        region=req.region,
        mode=req.mode,
        score=score,
        findings=all_findings,
        results=results,
    )

    # DB 저장 (DATABASE_URL 설정된 경우만)
    share_id: str | None = None
    if db is not None:
        try:
            row = AuditReport(
                target_url=str(req.url),
                place_name=req.place_name,
                region=req.region,
                mode=req.mode,
                score=score,
                findings=[f.model_dump() for f in all_findings],
                results=[r.model_dump() for r in results],
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            share_id = row.share_id
        except Exception:
            pass  # DB 저장 실패해도 리포트는 반환

    # share_id를 results 필드 raw에 실어서 전달 (프론트가 읽어 URL 구성)
    if share_id:
        report = report.model_copy(update={"share_id": share_id})

    return report


@app.get("/report/{share_id}", response_model=ReadinessReport)
async def get_report(share_id: str, db: AsyncSession = Depends(get_db)) -> ReadinessReport:
    from sqlalchemy import select
    result = await db.execute(
        select(AuditReport).where(AuditReport.share_id == share_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="리포트를 찾을 수 없습니다.")

    return ReadinessReport(
        target_url=row.target_url,
        place_name=row.place_name,
        region=row.region,
        mode=row.mode,
        score=row.score,
        findings=[Finding(**f) for f in row.findings],
        results=[SignalResult(**r) for r in row.results],
        generated_at=row.created_at,
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
