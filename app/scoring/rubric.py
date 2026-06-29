from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# unknown 처리 방식: 분모에서 제외.
# 평가된 항목의 가중치 합을 분모로 삼아 100점 정규화한다.
# Milestone 2 항목(milestone=2)은 현재 findings에 포함되지 않으므로
# 자동으로 unknown 처리되어 점수에 영향을 주지 않는다.


@dataclass(frozen=True)
class RubricItem:
    item_id: str
    weight: int
    mode: Literal["local", "brand"]
    milestone: int


# LOCAL 100점
# 플레이스&정보 일관성 22 / 구조화데이터&사이트 18(l_schema 12 + l_llms 6) /
# 지역 권위 22 / 리뷰 신호 24(M2) / 정보 최신성 14(M2)
LOCAL_RUBRIC: list[RubricItem] = [
    RubricItem("l_place",    22, "local", 1),
    RubricItem("l_schema",   12, "local", 1),
    RubricItem("l_llms",      6, "local", 1),
    RubricItem("l_comm",     22, "local", 1),
    RubricItem("l_review",   24, "local", 2),
    RubricItem("l_freshness", 14, "local", 2),
]

# BRAND 100점
# 크롤러접근 18 / 구조화데이터 16(b_org 8 + b_faq 4 + b_llms 4) /
# 제3자권위 18 / SEO기반 20(M2) / 콘텐츠구조 16(M2) / E-E-A-T 12(M2)
BRAND_RUBRIC: list[RubricItem] = [
    RubricItem("b_bots",    18, "brand", 1),
    RubricItem("b_org",      8, "brand", 1),
    RubricItem("b_faq",      4, "brand", 1),
    RubricItem("b_llms",     4, "brand", 1),
    RubricItem("b_comm",    18, "brand", 1),
    RubricItem("b_seo",     20, "brand", 2),
    RubricItem("b_content", 16, "brand", 2),
    RubricItem("b_eeat",    12, "brand", 2),
]

RUBRIC: dict[str, list[RubricItem]] = {
    "local": LOCAL_RUBRIC,
    "brand": BRAND_RUBRIC,
}
