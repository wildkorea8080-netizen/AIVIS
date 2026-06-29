from __future__ import annotations

from typing import Literal

from app.models.schemas import Finding
from app.scoring.rubric import RUBRIC

_STATE_WEIGHT: dict[str, float] = {"yes": 1.0, "partial": 0.5, "no": 0.0}


def compute_score(mode: Literal["local", "brand"], findings: list[Finding]) -> int:
    rubric = RUBRIC[mode]
    findings_map = {f.item_id: f.state for f in findings}

    total_weight = 0
    earned: float = 0.0

    for item in rubric:
        state = findings_map.get(item.item_id, "unknown")
        if state == "unknown":
            continue  # 분모에서 제외
        total_weight += item.weight
        earned += item.weight * _STATE_WEIGHT.get(state, 0.0)

    if total_weight == 0:
        return 0
    return round(earned / total_weight * 100)
