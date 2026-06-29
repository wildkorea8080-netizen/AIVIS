from __future__ import annotations

import httpx

from app.collectors.base import AuditContext, BaseCollector
from app.config import settings
from app.models.schemas import Finding, SignalResult

_KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


class PlaceCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        if not settings.kakao_rest_key:
            return SignalResult(
                collector="place",
                status="error",
                findings=[],
                error="KAKAO_REST_KEY 미설정",
            )

        if ctx.mode != "local":
            return SignalResult(
                collector="place",
                status="ok",
                findings=[
                    Finding(
                        item_id="l_place",
                        label="플레이스 등록",
                        state="unknown",
                        evidence="brand 모드 해당 없음",
                    )
                ],
            )

        query_parts = [ctx.region, ctx.place_name]
        query = " ".join(p for p in query_parts if p).strip()

        try:
            resp = await ctx.client.get(
                _KAKAO_KEYWORD_URL,
                params={"query": query, "size": 5},
                headers={"Authorization": f"KakaoAK {settings.kakao_rest_key}"},
            )
            resp.raise_for_status()
        except httpx.TimeoutException as e:
            return SignalResult(collector="place", status="error", findings=[], error=f"타임아웃: {e}")
        except Exception as e:
            return SignalResult(collector="place", status="error", findings=[], error=str(e))

        documents: list[dict] = resp.json().get("documents", [])

        exact = [d for d in documents if d.get("place_name") == ctx.place_name]
        partial_match = [d for d in documents if ctx.place_name and ctx.place_name in d.get("place_name", "")]

        if exact:
            state = "yes"
            hit = exact[0]
            evidence = f"정확 일치: {hit['place_name']} ({hit.get('address_name', '')})"
            raw = hit
        elif partial_match:
            state = "partial"
            hit = partial_match[0]
            evidence = f"유사 일치: {hit['place_name']}"
            raw = hit
        else:
            state = "no"
            evidence = f"'{query}' 검색 결과 없음"
            raw = {}

        return SignalResult(
            collector="place",
            status="ok",
            findings=[Finding(item_id="l_place", label="플레이스 등록", state=state, evidence=evidence)],
            raw=raw,
        )
