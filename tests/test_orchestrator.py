from __future__ import annotations

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_RICH_HTML = """
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"LocalBusiness","name":"테스트"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Menu"}
</script>
</head><body></body></html>
"""


@pytest.mark.asyncio
async def test_brand_basic_run():
    with respx.mock(assert_all_called=False):
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text="<html></html>"))
        respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
        respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
        # NAVER, KAKAO 키 없어서 error 로 빠짐
        resp = client.post("/audit", json={"url": "https://example.com", "mode": "brand"})
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert 0 <= data["score"] <= 100
    assert len(data["results"]) == 5


@pytest.mark.asyncio
async def test_local_requires_place_name():
    resp = client.post("/audit", json={"url": "https://example.com", "mode": "local"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_one_collector_failure_does_not_block():
    with respx.mock(assert_all_called=False):
        # schema: 500 error
        respx.get("https://example.com").mock(return_value=httpx.Response(500))
        respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
        respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
        resp = client.post("/audit", json={"url": "https://example.com", "mode": "brand"})
    assert resp.status_code == 200
    data = resp.json()
    statuses = {r["collector"]: r["status"] for r in data["results"]}
    assert statuses.get("schema") == "error"
    # 나머지는 ok or error(키 없음), 전체는 200
    assert data["score"] is not None


@pytest.mark.asyncio
async def test_score_in_range():
    with respx.mock(assert_all_called=False):
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text="<html></html>"))
        respx.get("https://example.com/llms.txt").mock(return_value=httpx.Response(404))
        respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
        resp = client.post("/audit", json={"url": "https://example.com", "mode": "brand"})
    assert resp.status_code == 200
    assert 0 <= resp.json()["score"] <= 100


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
