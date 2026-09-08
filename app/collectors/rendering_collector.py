from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup

from app.collectors.base import AuditContext, BaseCollector
from app.models.schemas import Finding, SignalResult

# CSR SPA 컨테이너 패턴 — 내용이 비어 있으면 JS 없이는 읽을 수 없음
_CSR_ROOTS = re.compile(r'id=["\'](root|__next|app|main-app)["\']', re.I)
_MIN_TEXT_LEN = 200  # 의미 있는 본문 최소 길이


def _assess(html: str) -> tuple[str, str]:
    """(state, evidence) 반환. state: yes(SSR) / partial / no(CSR)"""
    soup = BeautifulSoup(html, "lxml")

    # script/style/head 제거 후 본문 텍스트 추출
    for tag in soup(["script", "style", "head", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text_len = len(text)

    # CSR 루트 컨테이너가 비어 있는지 확인
    csr_containers = _CSR_ROOTS.findall(html)
    has_csr_root = bool(csr_containers)

    if text_len >= _MIN_TEXT_LEN:
        state = "yes"
        evidence = f"SSR 추정 — 본문 {text_len}자 (GPT봇 접근 가능)"
    elif has_csr_root and text_len < _MIN_TEXT_LEN:
        state = "no"
        evidence = f"CSR 추정 — 본문 {text_len}자 (GPT봇이 읽을 수 없을 가능성 높음)"
    else:
        state = "partial"
        evidence = f"본문 {text_len}자 — 부분 SSR 또는 확인 불충분"

    return state, evidence


class RenderingCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        item_id = "l_render" if ctx.mode == "local" else "b_render"
        label = "SSR/CSR 렌더링 (GPT봇 접근)"

        if not ctx.url:
            return SignalResult(
                collector="rendering",
                status="ok",
                findings=[Finding(item_id=item_id, label=label,
                                  state="unknown", evidence="URL 미입력")],
            )
        try:
            # 일반 봇처럼 JS 없이 HTML만 가져옴
            resp = await ctx.client.get(
                ctx.url,
                follow_redirects=True,
                headers={"User-Agent": "GPTBot/1.0"},
            )
            resp.raise_for_status()
        except httpx.TimeoutException as e:
            return SignalResult(collector="rendering", status="error", findings=[], error=f"타임아웃: {e}")
        except Exception as e:
            return SignalResult(collector="rendering", status="error", findings=[], error=str(e))

        import asyncio, functools
        loop = asyncio.get_event_loop()
        state, evidence = await loop.run_in_executor(
            None, functools.partial(_assess, resp.text)
        )
        return SignalResult(
            collector="rendering",
            status="ok",
            findings=[Finding(item_id=item_id, label=label, state=state, evidence=evidence)],
        )
