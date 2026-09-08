from __future__ import annotations

import json

import httpx
import pytest
import respx

from app.collectors.place_collector import PlaceCollector
from tests.conftest import make_ctx

_KAKAO_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


def _kakao_mock(documents: list[dict]):
    return respx.get(_KAKAO_URL).mock(
        return_value=httpx.Response(200, json={"documents": documents, "meta": {"total_count": len(documents)}})
    )


_HIT_EXACT = {"place_name": "테스트 카페", "address_name": "서울 강남구", "phone": "02-0000-0000", "category_name": "카페"}
_HIT_SIMILAR = {"place_name": "테스트 카페 강남점", "address_name": "서울 강남구"}
_HIT_UNRELATED = {"place_name": "완전히 다른 이름", "address_name": "부산"}


@pytest.mark.asyncio
async def test_exact_match_yes(monkeypatch):
    monkeypatch.setattr("app.collectors.place_collector.settings.kakao_rest_key", "fake_key")
    with respx.mock:
        _kakao_mock([_HIT_EXACT])
        async with httpx.AsyncClient() as client:
            result = await PlaceCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "yes"


@pytest.mark.asyncio
async def test_partial_match(monkeypatch):
    monkeypatch.setattr("app.collectors.place_collector.settings.kakao_rest_key", "fake_key")
    with respx.mock:
        _kakao_mock([_HIT_SIMILAR])
        async with httpx.AsyncClient() as client:
            result = await PlaceCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "partial"


@pytest.mark.asyncio
async def test_no_match(monkeypatch):
    monkeypatch.setattr("app.collectors.place_collector.settings.kakao_rest_key", "fake_key")
    with respx.mock:
        _kakao_mock([_HIT_UNRELATED])
        async with httpx.AsyncClient() as client:
            result = await PlaceCollector().collect(make_ctx(mode="local", client=client))
    assert result.findings[0].state == "no"


@pytest.mark.asyncio
async def test_no_key_reports_unknown():
    """키가 없으면 항목을 감추지 말고 unknown으로 노출한다 (점수 분모에서만 제외)."""
    with respx.mock:
        async with httpx.AsyncClient() as client:
            result = await PlaceCollector().collect(make_ctx(mode="local", client=client))
    assert result.status == "ok"
    assert result.findings[0].item_id == "l_place"
    assert result.findings[0].state == "unknown"
    assert "KAKAO" in result.findings[0].evidence


@pytest.mark.asyncio
async def test_brand_mode_unknown(monkeypatch):
    monkeypatch.setattr("app.collectors.place_collector.settings.kakao_rest_key", "fake_key")
    with respx.mock:
        async with httpx.AsyncClient() as client:
            result = await PlaceCollector().collect(make_ctx(mode="brand", client=client))
    assert result.status == "ok"
    assert result.findings[0].state == "unknown"


@pytest.mark.asyncio
async def test_timeout_error(monkeypatch):
    monkeypatch.setattr("app.collectors.place_collector.settings.kakao_rest_key", "fake_key")
    with respx.mock:
        respx.get(_KAKAO_URL).mock(side_effect=httpx.TimeoutException("timeout"))
        async with httpx.AsyncClient() as client:
            result = await PlaceCollector().collect(make_ctx(mode="local", client=client))
    assert result.status == "error"
