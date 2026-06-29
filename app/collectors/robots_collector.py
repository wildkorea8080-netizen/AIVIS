from __future__ import annotations

import httpx

from app.collectors.base import AuditContext, BaseCollector
from app.models.schemas import Finding, SignalResult

TARGET_BOTS = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"]


def _parse_blocked_bots(text: str) -> set[str]:
    """robots.txt 텍스트에서 Disallow: / 가 적용된 User-agent를 반환한다."""
    blocked: set[str] = set()
    current_agents: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            current_agents = []
            continue
        lower = line.lower()
        if lower.startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            current_agents.append(agent)
        elif lower.startswith("disallow:"):
            path = line.split(":", 1)[1].strip()
            if path == "/":
                for agent in current_agents:
                    blocked.add(agent)

    return blocked


class RobotsCollector(BaseCollector):
    async def collect(self, ctx: AuditContext) -> SignalResult:
        url = f"{ctx.origin}/robots.txt"
        try:
            resp = await ctx.client.get(url, follow_redirects=True)
        except httpx.TimeoutException as e:
            return _error("robots", f"타임아웃: {e}")
        except Exception as e:
            return _error("robots", str(e))

        if resp.status_code == 404:
            finding = Finding(
                item_id="b_bots",
                label="AI 크롤러 접근",
                state="yes",
                evidence="robots.txt 없음 (전체 허용)",
            )
            return SignalResult(
                collector="robots", status="ok", findings=[finding],
                raw={"robots_present": False},
            )

        if resp.status_code != 200:
            finding = Finding(
                item_id="b_bots",
                label="AI 크롤러 접근",
                state="unknown",
                evidence=f"HTTP {resp.status_code}",
            )
            return SignalResult(collector="robots", status="ok", findings=[finding])

        blocked_all = _parse_blocked_bots(resp.text)

        # *로 전체 차단인 경우 모든 봇에 적용
        if "*" in blocked_all:
            blocked_targets = list(TARGET_BOTS)
        else:
            blocked_targets = [b for b in TARGET_BOTS if b in blocked_all]

        if not blocked_targets:
            state = "yes"
            evidence = "모든 AI 봇 허용"
        elif len(blocked_targets) == len(TARGET_BOTS):
            state = "no"
            evidence = f"차단된 봇: {', '.join(blocked_targets)}"
        else:
            state = "partial"
            evidence = f"차단된 봇: {', '.join(blocked_targets)}"

        return SignalResult(
            collector="robots",
            status="ok",
            findings=[Finding(item_id="b_bots", label="AI 크롤러 접근", state=state, evidence=evidence)],
            raw={"blocked_bots": blocked_targets},
        )


def _error(collector: str, msg: str) -> SignalResult:
    return SignalResult(collector=collector, status="error", findings=[], error=msg)
