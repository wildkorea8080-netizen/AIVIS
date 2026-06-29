from __future__ import annotations

import asyncio
import functools
from typing import Any

import extruct
import httpx

from app.collectors.base import AuditContext, BaseCollector
from app.models.schemas import Finding, SignalResult

_LOCAL_TYPES = frozenset(
    {"LocalBusiness", "Restaurant", "Store", "FoodEstablishment", "Menu", "FAQPage"}
)
_BRAND_ORG_TYPES = frozenset({"Organization", "Corporation", "Brand", "Product"})


def _extract_types(html: str, base_url: str) -> set[str]:
    data = extruct.extract(
        html,
        base_url=base_url,
        syntaxes=["json-ld", "microdata"],
        uniform=True,
    )
    types_found: set[str] = set()
    for item in data.get("json-ld", []) + data.get("microdata", []):
        raw_type = item.get("@type") or []
        if isinstance(raw_type, str):
            raw_type = [raw_type]
        types_found.update(raw_type)
    return types_found


class SchemaCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        if not ctx.url:
            return SignalResult(collector="schema", status="ok",
                                findings=_make_findings(ctx.mode, set()))
        try:
            resp = await ctx.client.get(ctx.url, follow_redirects=True)
            resp.raise_for_status()
            html = resp.text
            base_url = str(resp.url)

            loop = asyncio.get_event_loop()
            types_found: set[str] = await loop.run_in_executor(
                None, functools.partial(_extract_types, html, base_url)
            )

            findings = _make_findings(ctx.mode, types_found)
            return SignalResult(
                collector="schema",
                status="ok",
                findings=findings,
                raw={"types_found": sorted(types_found)},
            )
        except httpx.TimeoutException as e:
            return _error("schema", f"타임아웃: {e}")
        except Exception as e:
            return _error("schema", str(e))


def _make_findings(mode: str, types_found: set[str]) -> list[Finding]:
    if mode == "local":
        matched = types_found & _LOCAL_TYPES
        if len(matched) >= 2:
            state = "yes"
        elif matched:
            state = "partial"
        else:
            state = "no"
        evidence = f"발견된 타입: {', '.join(sorted(matched))}" if matched else None
        return [Finding(item_id="l_schema", label="로컬 구조화 데이터", state=state, evidence=evidence)]
    else:
        faq = "FAQPage" in types_found
        org_matched = types_found & _BRAND_ORG_TYPES
        return [
            Finding(
                item_id="b_faq",
                label="FAQPage 스키마",
                state="yes" if faq else "no",
                evidence="FAQPage 발견" if faq else None,
            ),
            Finding(
                item_id="b_org",
                label="Organization/Product 스키마",
                state="yes" if org_matched else "no",
                evidence=f"타입: {', '.join(sorted(org_matched))}" if org_matched else None,
            ),
        ]


def _error(collector: str, msg: str) -> SignalResult:
    return SignalResult(collector=collector, status="error", findings=[], error=msg)
