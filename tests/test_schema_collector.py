from __future__ import annotations

import httpx
import pytest
import respx

from app.collectors.schema_collector import SchemaCollector
from tests.conftest import make_ctx

_LOCAL_BIZ_HTML = """
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"LocalBusiness","name":"테스트"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Menu","name":"메뉴"}
</script>
</head><body></body></html>
"""

_FAQPAGE_HTML = """
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","name":"FAQ"}
</script>
</head><body></body></html>
"""

_EMPTY_HTML = "<html><body></body></html>"

_ORG_HTML = """
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"ACME"}
</script>
</head><body></body></html>
"""


@pytest.mark.asyncio
async def test_local_yes_two_types():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_LOCAL_BIZ_HTML))
        async with httpx.AsyncClient() as client:
            ctx = make_ctx(mode="local", client=client)
            result = await SchemaCollector().collect(ctx)
    assert result.status == "ok"
    assert result.findings[0].item_id == "l_schema"
    assert result.findings[0].state == "yes"


@pytest.mark.asyncio
async def test_local_partial_one_type():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_FAQPAGE_HTML))
        async with httpx.AsyncClient() as client:
            ctx = make_ctx(mode="local", client=client)
            result = await SchemaCollector().collect(ctx)
    assert result.findings[0].state == "partial"


@pytest.mark.asyncio
async def test_local_no_schema():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_EMPTY_HTML))
        async with httpx.AsyncClient() as client:
            ctx = make_ctx(mode="local", client=client)
            result = await SchemaCollector().collect(ctx)
    assert result.findings[0].state == "no"


@pytest.mark.asyncio
async def test_brand_faq_yes():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_FAQPAGE_HTML))
        async with httpx.AsyncClient() as client:
            ctx = make_ctx(mode="brand", client=client)
            result = await SchemaCollector().collect(ctx)
    ids = {f.item_id: f.state for f in result.findings}
    assert ids["b_faq"] == "yes"
    assert ids["b_org"] == "no"


@pytest.mark.asyncio
async def test_brand_org_yes():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text=_ORG_HTML))
        async with httpx.AsyncClient() as client:
            ctx = make_ctx(mode="brand", client=client)
            result = await SchemaCollector().collect(ctx)
    ids = {f.item_id: f.state for f in result.findings}
    assert ids["b_org"] == "yes"
    assert ids["b_faq"] == "no"


@pytest.mark.asyncio
async def test_http_error():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(500))
        async with httpx.AsyncClient() as client:
            ctx = make_ctx(mode="local", client=client)
            result = await SchemaCollector().collect(ctx)
    assert result.status == "error"


@pytest.mark.asyncio
async def test_timeout():
    with respx.mock:
        respx.get("https://example.com").mock(side_effect=httpx.TimeoutException("timeout"))
        async with httpx.AsyncClient() as client:
            ctx = make_ctx(mode="local", client=client)
            result = await SchemaCollector().collect(ctx)
    assert result.status == "error"
