"""AI 응답에서 추천된 업체명을 순서대로 추출한다.

순수 모듈 — I/O·DB·설정에 의존하지 않으므로 단위 테스트가 쉽다.

엔진마다 서식 습관이 달라(Gemini는 볼드, Perplexity는 [1] 인용 표기) 형식을
완벽히 지키지 않는다. 그런 응답에서는 쓰레기를 만들어내지 말고 빈 리스트로
물러나는 것이 이 파서의 계약이다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_MAX_NAME_LEN = 40

# "1. 이름" / "2) 이름" 형태의 목록 항목
_LIST_ITEM = re.compile(r"^\s*(\d{1,2})\s*[.)]\s*(.+?)\s*$")

# [텍스트](url) -> 텍스트
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
# Perplexity 등이 붙이는 [1], [2] 인용 표기
_CITATION = re.compile(r"\[\d+\]")
# 마크다운 강조·코드·헤더 기호
_MD_NOISE = re.compile(r"[*_`#]+")

# 업체명이 끝나고 설명이 시작되는 지점
_CUT = re.compile(r"[(（:：]|\s+[-–—|·]\s*|\s{2,}")

# 이름 앞뒤에 붙는 따옴표·괄호류
_TRIM_CHARS = " \t\"'“”‘’「」『』<>《》【】·-–—"

# 이름이 아니라 문장인 경우를 걸러낸다.
# '니다'는 격식체 종결의 공통 꼬리(합니다/습니다/다릅니다/드립니다…)라 하나로 묶는다.
_SENTENCE_TAIL = re.compile(r"(하세요|해보세요|세요|해요|하기|니다)$")

# 목차·안내 문구
_BOILERPLATE = frozenset({
    "추천", "다음", "참고", "정리", "결론", "요약", "주의사항", "마무리",
    "참고사항", "추천업체", "추천목록", "기타",
})

_HAS_LETTER = re.compile(r"[가-힣a-zA-Z]")


@dataclass(frozen=True)
class ParsedMention:
    rank: int        # 목록에서의 순번 (1-based)
    name_raw: str    # AI가 쓴 그대로
    name_key: str    # 집계용 정규화 키


def normalize_name(name: str) -> str:
    """집계 키를 만든다. 소문자화 + 공백 제거 + 말미 지점 표기 제거.

    '이루다치과' / '이루다 치과' / '이루다치과 ' -> '이루다치과'
    지역 접두어까지는 벗기지 않는다('강남 이루다치과' -> '강남이루다치과').
    실제 데이터를 보기 전의 별칭 규칙은 추측일 뿐이므로 v1에서는 넣지 않는다.
    """
    key = re.sub(r"\s+", "", name).lower()
    key = re.sub(r"(지점|점)$", "", key)
    return key


def _clean_item(item: str) -> str:
    """목록 항목 한 줄에서 업체명만 남긴다. 이름이 아니면 빈 문자열."""
    text = _MD_LINK.sub(r"\1", item)
    text = _CITATION.sub("", text)
    text = _MD_NOISE.sub("", text)

    cut = _CUT.search(text)
    if cut:
        text = text[: cut.start()]

    name = text.strip(_TRIM_CHARS).strip()

    if not name or len(name) > _MAX_NAME_LEN:
        return ""
    if not _HAS_LETTER.search(name):
        return ""
    if _SENTENCE_TAIL.search(name):
        return ""
    if normalize_name(name) in _BOILERPLATE:
        return ""
    return name


def parse_recommendations(text: str) -> list[ParsedMention]:
    """번호 목록에서 추천 업체를 순서대로 뽑는다.

    형식을 지키지 않은 응답이면 빈 리스트를 반환한다.
    같은 업체가 여러 번 나오면 가장 앞선 순번만 남긴다.
    """
    if not text:
        return []

    mentions: list[ParsedMention] = []
    seen: set[str] = set()

    for line in text.splitlines():
        matched = _LIST_ITEM.match(line)
        if not matched:
            continue

        name = _clean_item(matched.group(2))
        if not name:
            continue

        key = normalize_name(name)
        if key in seen:
            continue
        seen.add(key)

        mentions.append(ParsedMention(rank=len(mentions) + 1, name_raw=name, name_key=key))

    return mentions


def matches_brand(name_key: str, brand: str) -> bool:
    """추출된 업체명이 내 브랜드인지 판정.

    'AI가 쓴 이름'과 '등록한 키워드'는 지역 접두어 유무로 자주 어긋나므로
    (예: 키워드 '이루다치과' vs 응답 '강남 이루다치과') 부분 포함으로 본다.
    """
    brand_key = normalize_name(brand)
    if not brand_key or not name_key:
        return False
    return brand_key in name_key or name_key in brand_key
