from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

import httpx

from app.models.schemas import SignalResult


@dataclass
class AuditContext:
    url: str | None          # LOCAL 모드에서 URL 없을 수 있음
    origin: str | None
    place_name: str | None
    region: str | None
    mode: Literal["local", "brand"]
    client: httpx.AsyncClient

    @classmethod
    def from_request(
        cls,
        url: str | None,
        place_name: str | None,
        region: str | None,
        mode: Literal["local", "brand"],
        client: httpx.AsyncClient,
    ) -> AuditContext:
        origin: str | None = None
        if url:
            parsed = httpx.URL(url)
            origin = f"{parsed.scheme}://{parsed.host}"
            if parsed.port:
                origin += f":{parsed.port}"
        return cls(
            url=url,
            origin=origin,
            place_name=place_name,
            region=region,
            mode=mode,
            client=client,
        )

    # 하위호환: 기존 from_url 유지
    @classmethod
    def from_url(
        cls,
        url: str,
        place_name: str | None,
        region: str | None,
        mode: Literal["local", "brand"],
        client: httpx.AsyncClient,
    ) -> AuditContext:
        return cls.from_request(url, place_name, region, mode, client)


class BaseCollector(ABC):
    @abstractmethod
    async def collect(self, ctx: AuditContext) -> SignalResult: ...
