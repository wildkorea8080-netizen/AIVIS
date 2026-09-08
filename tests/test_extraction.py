from __future__ import annotations

import pytest

from app.monitor.extraction import (
    matches_brand,
    normalize_name,
    parse_recommendations,
)


# ── 엔진별 실제 서식 습관 ─────────────────────────────────────

_PLAIN = """강남역 근처 임플란트 잘하는 치과를 추천드립니다.

1. 이루다치과 - 임플란트 전문으로 20년 경력
2. 서울그랜드치과 - 디지털 임플란트 장비 보유
3. 강남연세치과 - 야간 진료 가능

방문 전 예약을 권장합니다.
"""

# Gemini: 항목을 볼드로 감싸는 습관
_BOLD = """추천 목록입니다.

1. **이루다치과** — 임플란트 전문
2. **서울그랜드치과**: 최신 장비
3. **강남연세치과** (야간진료)
"""

# Perplexity: 검색 근거 [n] 인용 표기를 섞음
_CITED = """1. 이루다치과[1] - 임플란트 특화[2]
2. 서울그랜드치과[3] - 강남역 3번 출구
3. [강남연세치과](https://example.com/clinic) - 야간 진료
"""

# 형식을 지키지 않은 산문 응답
_PROSE = """강남역 근처에는 여러 치과가 있습니다. 이루다치과는 임플란트로 유명하고,
서울그랜드치과도 평가가 좋습니다. 다만 방문 전 상담을 받아보시길 권합니다.
"""


def _names(text: str) -> list[str]:
    return [m.name_raw for m in parse_recommendations(text)]


def test_plain_numbered_list():
    mentions = parse_recommendations(_PLAIN)
    assert [m.name_raw for m in mentions] == ["이루다치과", "서울그랜드치과", "강남연세치과"]
    assert [m.rank for m in mentions] == [1, 2, 3]


def test_bold_markdown_is_stripped():
    assert _names(_BOLD) == ["이루다치과", "서울그랜드치과", "강남연세치과"]


def test_citation_markers_and_links_are_stripped():
    assert _names(_CITED) == ["이루다치과", "서울그랜드치과", "강남연세치과"]


def test_prose_without_list_yields_nothing():
    """형식 미준수 응답에서는 추측하지 말고 물러난다."""
    assert parse_recommendations(_PROSE) == []


def test_empty_text():
    assert parse_recommendations("") == []


@pytest.mark.parametrize("line", [
    "1. 방문 전 예약을 확인하세요",
    "2. 상담을 먼저 받아보시길 권합니다",
    "3. 가격은 병원마다 다릅니다",
])
def test_sentences_are_not_names(line):
    assert parse_recommendations(line) == []


@pytest.mark.parametrize("line", ["1. 추천", "2. 참고사항", "3. 정리"])
def test_boilerplate_headings_rejected(line):
    assert parse_recommendations(line) == []


def test_overlong_item_rejected():
    long_item = "1. " + "가" * 41
    assert parse_recommendations(long_item) == []


def test_duplicate_keeps_first_rank():
    text = "1. 이루다치과 - 설명\n2. 서울그랜드치과 - 설명\n3. 이루다 치과 - 다시 언급\n"
    mentions = parse_recommendations(text)
    assert [m.name_raw for m in mentions] == ["이루다치과", "서울그랜드치과"]
    assert [m.rank for m in mentions] == [1, 2]


def test_rank_is_positional_not_the_written_number():
    """중간 항목이 이름이 아니면 그다음 업체가 2위가 된다."""
    text = "1. 이루다치과 - 설명\n2. 참고\n3. 서울그랜드치과 - 설명\n"
    mentions = parse_recommendations(text)
    assert [(m.name_raw, m.rank) for m in mentions] == [("이루다치과", 1), ("서울그랜드치과", 2)]


def test_paren_suffix_is_cut():
    assert _names("1. 이루다치과(강남점) - 설명") == ["이루다치과"]


def test_hyphen_inside_name_is_kept():
    assert _names("1. S-라인치과 - 교정 전문") == ["S-라인치과"]


def test_closing_paren_format():
    assert _names("1) 이루다치과 - 설명\n2) 서울그랜드치과 - 설명") == ["이루다치과", "서울그랜드치과"]


# ── normalize_name ───────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("이루다치과", "이루다치과"),
    ("이루다 치과", "이루다치과"),
    ("  이루다치과  ", "이루다치과"),
    ("이루다치과 강남점", "이루다치과강남"),
    ("Iruda Clinic", "irudaclinic"),
])
def test_normalize_name(raw, expected):
    assert normalize_name(raw) == expected


# ── matches_brand ────────────────────────────────────────────

@pytest.mark.parametrize("name,brand", [
    ("이루다치과", "이루다치과"),
    ("강남이루다치과", "이루다치과"),   # AI가 지역 접두어를 붙인 경우
    ("이루다치과", "강남 이루다치과"),  # 사용자가 지역까지 등록한 경우
])
def test_matches_brand_true(name, brand):
    assert matches_brand(normalize_name(name), brand) is True


@pytest.mark.parametrize("name,brand", [
    ("서울그랜드치과", "이루다치과"),
    ("이루다치과", ""),
])
def test_matches_brand_false(name, brand):
    assert matches_brand(normalize_name(name), brand) is False
