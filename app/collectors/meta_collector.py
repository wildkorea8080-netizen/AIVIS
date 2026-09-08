from __future__ import annotations

import re
from typing import Literal

import httpx
from bs4 import BeautifulSoup

from app.collectors.base import AuditContext, BaseCollector
from app.models.schemas import Finding, SignalResult

_TITLE_MIN = 20
_TITLE_MAX = 65
_DESC_MIN  = 50
_DESC_MAX  = 160


def _state(score: int, total: int) -> Literal["yes", "partial", "no"]:
    ratio = score / total if total else 0
    if ratio >= 0.8:
        return "yes"
    if ratio >= 0.4:
        return "partial"
    return "no"


def _analyze(html: str) -> tuple[Literal["yes", "partial", "no"], str]:
    soup = BeautifulSoup(html, "lxml")
    score = 0
    total = 5
    issues: list[str] = []

    # 1. title
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""
    if _TITLE_MIN <= len(title_text) <= _TITLE_MAX:
        score += 1
    else:
        issues.append(f"title {len(title_text)}자({'없음' if not title_text else '권장 범위 벗어남'})")

    # 2. meta description
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    desc = desc_tag.get("content", "") if desc_tag else ""
    if _DESC_MIN <= len(desc) <= _DESC_MAX:
        score += 1
    else:
        issues.append(f"description {len(desc)}자({'없음' if not desc else '권장 범위 벗어남'})")

    # 3. H1 정확히 1개
    h1s = soup.find_all("h1")
    if len(h1s) == 1:
        score += 1
    else:
        issues.append(f"H1 {len(h1s)}개(권장: 1개)")

    # 4. H2 존재
    h2s = soup.find_all("h2")
    if h2s:
        score += 1
    else:
        issues.append("H2 없음")

    # 5. 이미지 alt 텍스트 (80% 이상)
    imgs = soup.find_all("img")
    if imgs:
        with_alt = sum(1 for img in imgs if img.get("alt", "").strip())
        alt_ratio = with_alt / len(imgs)
        if alt_ratio >= 0.8:
            score += 1
        else:
            issues.append(f"이미지 alt 누락 {len(imgs)-with_alt}/{len(imgs)}개")
    else:
        score += 1  # 이미지 없으면 해당 없음

    state = _state(score, total)
    evidence = f"{score}/{total}개 통과" + (f" — {', '.join(issues[:2])}" if issues else "")
    return state, evidence


class MetaTagCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        item_id = "l_meta" if ctx.mode == "local" else "b_meta"
        label = "메타·콘텐츠 구조"

        if not ctx.url:
            return SignalResult(
                collector="meta",
                status="ok",
                findings=[Finding(item_id=item_id, label=label,
                                  state="unknown", evidence="URL 미입력")],
            )
        try:
            resp = await ctx.client.get(ctx.url, follow_redirects=True)
            resp.raise_for_status()
        except httpx.TimeoutException as e:
            return SignalResult(collector="meta", status="error", findings=[], error=f"타임아웃: {e}")
        except Exception as e:
            return SignalResult(collector="meta", status="error", findings=[], error=str(e))

        import asyncio, functools
        loop = asyncio.get_event_loop()
        state, evidence = await loop.run_in_executor(
            None, functools.partial(_analyze, resp.text)
        )
        return SignalResult(
            collector="meta",
            status="ok",
            findings=[Finding(item_id=item_id, label=label, state=state, evidence=evidence)],
        )
