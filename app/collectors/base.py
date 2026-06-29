from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

import httpx

from app.models.schemas import SignalResult


@dataclass
class AuditContext:
    url: str
    origin: str
    place_name: str | None
    region: str | None
    mode: Literal["local", "brand"]
    client: httpx.AsyncClient

    @classmethod
    def from_url(
        cls,
        url: str,
        place_name: str | None,
        region: str | None,
        mode: Literal["local", "brand"],
        client: httpx.AsyncClient,
    ) -> AuditContext:
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


class BaseCollector(ABC):
    @abstractmethod
    async def collect(self, ctx: AuditContext) -> SignalResult: ...
