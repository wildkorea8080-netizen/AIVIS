from __future__ import annotations

import httpx
import pytest
import respx

from app.collectors.mention_collector import MentionCollector, _BLOG_URL, _CAFE_URL
from tests.conftest import make_ctx


def _naver_mock(blog_total: int, cafe_total: int):
    respx.get(_BLOG_URL).mock(
        return_value=httpx.Response(200, json={"total": blog_total, "items": []})
    )
    respx.get(_CAFE_URL).mock(
        return_value=httpx.Response(200, json={"total": cafe_total, "items": []})
    )


def _patch_naver(monkeypatch):
    monkeypatch.setattr("app.collectors.mention_collector.settings.naver_client_id", "fake_id")
    monkeypatch.setattr("app.collectors.mention_collector.settings.naver_client_secret", "fake_secret")


@pytest.mark.asyncio
async def test_local_yes(monkeypatch):
    _patch_naver(monkeypatch)
    with respx.mock:
        _naver_mock(8, 5)
        async with httpx.AsyncClient() as client:
            result = await MentionCollector().collect(make_ctx(mode="local", client=client))
    f = result.findings[0]
    assert f.item_id == "l_comm"
    assert f.state == "yes"


@pytest.mark.asyncio
async def test_local_partial(monkeypatch):
    _patch_naver(monkeypatch)
    with respx.mock:
        _naver_mock(2, 1)
        async with httpx.AsyncClient() as client:
            result = await MentionCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "partial"


@pytest.mark.asyncio
async def test_local_no(monkeypatch):
    _patch_naver(monkeypatch)
    with respx.mock:
        _naver_mock(0, 0)
        async with httpx.AsyncClient() as client:
            result = await MentionCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "no"


@pytest.mark.asyncio
async def test_no_key_reports_unknown():
    """키가 없으면 항목을 감추지 말고 unknown으로 노출한다 (점수 분모에서만 제외)."""
    with respx.mock:
        async with httpx.AsyncClient() as client:
            result = await MentionCollector().collect(make_ctx(mode="local", client=client))
    assert result.status == "ok"
    assert result.findings[0].item_id == "l_comm"
    assert result.findings[0].state == "unknown"
    assert "NAVER" in result.findings[0].evidence


@pytest.mark.asyncio
async def test_brand_item_id(monkeypatch):
    _patch_naver(monkeypatch)
    with respx.mock:
        _naver_mock(10, 5)
        async with httpx.AsyncClient() as client:
            result = await MentionCollector().collect(make_ctx(mode="brand", client=client))
    assert result.findings[0].item_id == "b_comm"
    assert result.findings[0].state == "yes"
