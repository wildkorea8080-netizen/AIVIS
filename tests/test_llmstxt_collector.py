from __future__ import annotations

import httpx
import pytest
import respx

from app.collectors.llmstxt_collector import LlmsTxtCollector
from tests.conftest import make_ctx

_RICH_CONTENT = "x" * 200
_THIN_CONTENT = "hi"


@pytest.mark.asyncio
async def test_local_yes():
    with respx.mock:
        respx.get("https://example.com/llms.txt").mock(
            return_value=httpx.Response(200, text=_RICH_CONTENT)
        )
        async with httpx.AsyncClient() as client:
            result = await LlmsTxtCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].item_id == "l_llms"
    assert result.findings[0].state == "yes"


@pytest.mark.asyncio
async def test_local_partial():
    with respx.mock:
        respx.get("https://example.com/llms.txt").mock(
            return_value=httpx.Response(200, text=_THIN_CONTENT)
        )
        async with httpx.AsyncClient() as client:
            result = await LlmsTxtCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "partial"


@pytest.mark.asyncio
async def test_local_no():
    with respx.mock:
        respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
        async with httpx.AsyncClient() as client:
            result = await LlmsTxtCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "no"


@pytest.mark.asyncio
async def test_brand_item_id():
    with respx.mock:
        respx.get("https://example.com/llms.txt").mock(
            return_value=httpx.Response(200, text=_RICH_CONTENT)
        )
        async with httpx.AsyncClient() as client:
            result = await LlmsTxtCollector().collect(make_ctx(mode="brand", client=client))
    assert result.findings[0].item_id == "b_llms"
    assert result.findings[0].state == "yes"


@pytest.mark.asyncio
async def test_timeout_unknown():
    with respx.mock:
        respx.get("https://example.com/llms.txt").mock(
            side_effect=httpx.TimeoutException("timeout")
        )
        async with httpx.AsyncClient() as client:
            result = await LlmsTxtCollector().collect(make_ctx(mode="local", client=client))
    assert result.status == "ok"
    assert result.findings[0].state == "unknown"


@pytest.mark.asyncio
async def test_other_status_unknown():
    with respx.mock:
        respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(503))
        async with httpx.AsyncClient() as client:
            result = await LlmsTxtCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "unknown"
