from __future__ import annotations

import httpx
import pytest
import respx

from app.collectors.base import AuditContext


def make_ctx(
    url: str = "https://example.com",
    place_name: str | None = "테스트 카페",
    region: str | None = "서울",
    mode: str = "local",
    client: httpx.AsyncClient | None = None,
) -> AuditContext:
    if client is None:
        client = httpx.AsyncClient()
    return AuditContext.from_url(
        url=url,
        place_name=place_name,
        region=region,
        mode=mode,  # type: ignore[arg-type]
        client=client,
    )
