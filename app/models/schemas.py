from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, HttpUrl, model_validator

State = Literal["yes", "partial", "no", "unknown"]


class Finding(BaseModel):
    item_id: str
    label: str
    state: State
    evidence: str | None = None


class SignalResult(BaseModel):
    collector: str
    status: Literal["ok", "partial", "error"]
    findings: list[Finding]
    raw: dict = {}
    error: str | None = None


class ReadinessReport(BaseModel):
    target_url: str
    place_name: str | None
    region: str | None
    mode: Literal["local", "brand"]
    score: int
    findings: list[Finding]
    results: list[SignalResult]
    generated_at: datetime = None  # type: ignore[assignment]
    share_id: str | None = None

    def model_post_init(self, __context: object) -> None:
        if self.generated_at is None:
            object.__setattr__(self, "generated_at", datetime.now(timezone.utc))


class AuditRequest(BaseModel):
    url: HttpUrl | None = None   # LOCAL 모드에서 선택 입력
    place_name: str | None = None
    region: str | None = None
    mode: Literal["local", "brand"] = "brand"

    @model_validator(mode="after")
    def validate_inputs(self) -> AuditRequest:
        if self.mode == "local" and not self.place_name:
            raise ValueError("mode=local 은 place_name 이 필요합니다")
        if self.mode == "brand" and not self.url:
            raise ValueError("mode=brand 는 url 이 필요합니다")
        return self
