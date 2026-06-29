from __future__ import annotations

import asyncio

import httpx

from app.collectors.base import AuditContext, BaseCollector
from app.config import settings
from app.models.schemas import Finding, SignalResult

_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"
_CAFE_URL = "https://openapi.naver.com/v1/search/cafearticle.json"


class MentionCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        if not (settings.naver_client_id and settings.naver_client_secret):
            return SignalResult(
                collector="mention",
                status="error",
                findings=[],
                error="NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 미설정",
            )

        query_parts = [ctx.place_name, ctx.region]
        query = " ".join(p for p in query_parts if p).strip()
        if not query:
            return SignalResult(
                collector="mention",
                status="error",
                findings=[],
                error="검색어 없음 (place_name, region 모두 미입력)",
            )

        headers = {
            "X-Naver-Client-Id": settings.naver_client_id,
            "X-Naver-Client-Secret": settings.naver_client_secret,
        }

        try:
            blog_res, cafe_res = await asyncio.gather(
                ctx.client.get(_BLOG_URL, params={"query": query, "display": 1}, headers=headers),
                ctx.client.get(_CAFE_URL, params={"query": query, "display": 1}, headers=headers),
            )
            blog_total: int = blog_res.json().get("total", 0)
            cafe_total: int = cafe_res.json().get("total", 0)
        except httpx.TimeoutException as e:
            return SignalResult(collector="mention", status="error", findings=[], error=f"타임아웃: {e}")
        except Exception as e:
            return SignalResult(collector="mention", status="error", findings=[], error=str(e))

        total = blog_total + cafe_total

        if total >= settings.mention_threshold_yes:
            state = "yes"
        elif total >= settings.mention_threshold_partial:
            state = "partial"
        else:
            state = "no"

        item_id = "l_comm" if ctx.mode == "local" else "b_comm"
        evidence = f"블로그 {blog_total}건 + 카페 {cafe_total}건 = 총 {total}건"

        return SignalResult(
            collector="mention",
            status="ok",
            findings=[Finding(item_id=item_id, label="커뮤니티 언급", state=state, evidence=evidence)],
            raw={"blog_total": blog_total, "cafe_total": cafe_total, "total": total, "query": query},
        )
