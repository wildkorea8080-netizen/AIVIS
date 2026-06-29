from __future__ import annotations

import httpx
import pytest
import respx

from app.collectors.robots_collector import RobotsCollector
from app.collectors.base import AuditContext

_ALLOW_ALL = "User-agent: *\nAllow: /"
_BLOCK_GPTBOT = "User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /"
_BLOCK_WILDCARD = "User-agent: *\nDisallow: /"
_BLOCK_ALL_FIVE = "\n\n".join(
    f"User-agent: {bot}\nDisallow: /"
    for bot in ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"]
)

_ROBOTS_URL = "https://example.com/robots.txt"


def _make_ctx(client: httpx.AsyncClient) -> AuditContext:
    return AuditContext(
        url="https://example.com",
        origin="https://example.com",
        place_name=None,
        region=None,
        mode="brand",
        client=client,
    )


async def _collect(text: str, status: int = 200) -> str:
    async with respx.MockRouter(assert_all_called=False) as mock:
        mock.get(_ROBOTS_URL).mock(return_value=httpx.Response(status, text=text))
        async with httpx.AsyncClient() as client:
            result = await RobotsCollector().collect(_make_ctx(client))
    return result.findings[0].state


@pytest.mark.asyncio
async def test_no_robots_yes():
    assert await _collect("", status=404) == "yes"


@pytest.mark.asyncio
async def test_allow_all_yes():
    assert await _collect(_ALLOW_ALL) == "yes"


@pytest.mark.asyncio
async def test_one_bot_blocked_partial():
    assert await _collect(_BLOCK_GPTBOT) == "partial"


@pytest.mark.asyncio
async def test_wildcard_block_no():
    assert await _collect(_BLOCK_WILDCARD) == "no"


@pytest.mark.asyncio
async def test_all_five_blocked_no():
    assert await _collect(_BLOCK_ALL_FIVE) == "no"
