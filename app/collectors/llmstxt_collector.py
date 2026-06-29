from __future__ import annotations

import httpx

from app.collectors.base import AuditContext, BaseCollector
from app.models.schemas import Finding, SignalResult

_MIN_CONTENT_LEN = 100  # 이 이상이어야 yes


class LlmsTxtCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        item_id = "l_llms" if ctx.mode == "local" else "b_llms"
        url = f"{ctx.origin}/llms.txt"

        try:
            resp = await ctx.client.get(url, follow_redirects=True)
        except httpx.TimeoutException:
            state, evidence = "unknown", "요청 타임아웃"
        except Exception as e:
            state, evidence = "unknown", str(e)
        else:
            if resp.status_code == 200:
                content = resp.text.strip()
                if len(content) >= _MIN_CONTENT_LEN:
                    state = "yes"
                    evidence = f"{len(content)}자"
                else:
                    state = "partial"
                    evidence = f"파일 존재하나 내용 부족 ({len(content)}자)"
            elif resp.status_code == 404:
                state, evidence = "no", "404 Not Found"
            else:
                state, evidence = "unknown", f"HTTP {resp.status_code}"

        return SignalResult(
            collector="llmstxt",
            status="ok",
            findings=[Finding(item_id=item_id, label="llms.txt", state=state, evidence=evidence)],
        )
