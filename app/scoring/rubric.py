from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# unknown 처리: 분모에서 제외 → 평가된 항목 기준으로 100점 정규화.
# milestone=2 항목은 아직 findings에 포함되지 않으므로 자동으로 unknown 처리됨.


@dataclass(frozen=True)
class RubricItem:
    item_id: str
    weight: int
    mode: Literal["local", "brand"]
    milestone: int


# LOCAL 100점
# 플레이스 20 / 구조화데이터 10 / llms 5 / 커뮤니티 18
# 메타·콘텐츠구조 6 / 사이트맵 3 / 렌더링 3   (M1 신규)
# 리뷰신호 22 / 최신성 13  (M2)
LOCAL_RUBRIC: list[RubricItem] = [
    RubricItem("l_place",    20, "local", 1),
    RubricItem("l_schema",   10, "local", 1),
    RubricItem("l_llms",      5, "local", 1),
    RubricItem("l_comm",     18, "local", 1),
    RubricItem("l_meta",      6, "local", 1),   # 신규: 메타태그·H태그
    RubricItem("l_sitemap",   3, "local", 1),   # 신규: sitemap.xml
    RubricItem("l_render",    3, "local", 1),   # 신규: SSR/CSR
    RubricItem("l_review",   22, "local", 2),
    RubricItem("l_freshness", 13, "local", 2),
]

# BRAND 100점
# 크롤러접근 14 / 구조화데이터 13(b_org 7+b_faq 3+b_llms 3) / 커뮤니티 15
# 메타·콘텐츠구조 8 / 사이트맵 4 / 렌더링 4   (M1 신규)
# SEO기반 12 / 콘텐츠구조 16 / E-E-A-T 14   (M2)
BRAND_RUBRIC: list[RubricItem] = [
    RubricItem("b_bots",    14, "brand", 1),
    RubricItem("b_org",      7, "brand", 1),
    RubricItem("b_faq",      3, "brand", 1),
    RubricItem("b_llms",     3, "brand", 1),
    RubricItem("b_comm",    15, "brand", 1),
    RubricItem("b_meta",     8, "brand", 1),    # 신규: 메타태그·H태그
    RubricItem("b_sitemap",  4, "brand", 1),    # 신규: sitemap.xml
    RubricItem("b_render",   4, "brand", 1),    # 신규: SSR/CSR
    RubricItem("b_seo",     12, "brand", 2),
    RubricItem("b_content", 16, "brand", 2),
    RubricItem("b_eeat",    14, "brand", 2),
]

RUBRIC: dict[str, list[RubricItem]] = {
    "local": LOCAL_RUBRIC,
    "brand": BRAND_RUBRIC,
}
