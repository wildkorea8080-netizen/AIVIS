"""AI 모델별 질문 호출 + 브랜드 언급 여부 판정."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Awaitable, Callable

import httpx

from app.config import settings

_SYSTEM = (
    "당신은 한국 소비자에게 비즈니스·서비스를 추천하는 AI 어시스턴트입니다. "
    "질문에 구체적인 이름을 들어 추천해주세요."
)
_MAX_TOKENS = 800
_TIMEOUT = 30.0


@dataclass
class AiResponse:
    model: str
    mentioned: bool
    rank: int | None    # 몇 번째 추천으로 언급됐는지 (1-based), 없으면 None
    snippet: str | None # 언급된 문장 발췌


def _detect_mention(text: str, brand: str) -> tuple[bool, int | None, str | None]:
    """응답 텍스트에서 브랜드 언급 여부와 순위를 판정."""
    lower_text = text.lower()
    lower_brand = brand.lower()

    if lower_brand not in lower_text:
        return False, None, None

    sentences = re.split(r"[.。\n]", text)
    snippet = next((s.strip() for s in sentences if lower_brand in s.lower()), None)
    if snippet and len(snippet) > 200:
        snippet = snippet[:200] + "..."

    # 순위 추정: 번호 목록(1. 2. 3.)에서 브랜드가 몇 번째인지
    rank = None
    numbered = re.findall(r"(\d+)[.)\s].*?" + re.escape(lower_brand), lower_text)
    if numbered:
        rank = int(numbered[0])

    return True, rank, snippet


# ── 엔진별 호출 ───────────────────────────────────────────────

async def ask_chatgpt(question: str, brand: str) -> AiResponse:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": question},
        ],
        max_tokens=_MAX_TOKENS,
        temperature=0.3,
    )
    return _build("chatgpt", resp.choices[0].message.content or "", brand)


async def ask_claude(question: str, brand: str) -> AiResponse:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    resp = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=_MAX_TOKENS,
        system=_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    text = resp.content[0].text if resp.content else ""
    return _build("claude", text, brand)


async def ask_gemini(question: str, brand: str) -> AiResponse:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            url,
            params={"key": settings.gemini_api_key},
            json={
                "systemInstruction": {"parts": [{"text": _SYSTEM}]},
                "contents": [{"parts": [{"text": question}]}],
                "generationConfig": {"maxOutputTokens": _MAX_TOKENS, "temperature": 0.3},
            },
        )
        resp.raise_for_status()
        data = resp.json()

    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    return _build("gemini", text, brand)


async def ask_perplexity(question: str, brand: str) -> AiResponse:
    text = await _openai_compatible(
        base_url="https://api.perplexity.ai",
        api_key=settings.perplexity_api_key,
        model="sonar",
        question=question,
    )
    return _build("perplexity", text, brand)


async def ask_grok(question: str, brand: str) -> AiResponse:
    text = await _openai_compatible(
        base_url="https://api.x.ai/v1",
        api_key=settings.xai_api_key,
        model="grok-3",
        question=question,
    )
    return _build("grok", text, brand)


async def _openai_compatible(base_url: str, api_key: str, model: str, question: str) -> str:
    """OpenAI 호환 chat/completions 엔드포인트 공통 호출 (Perplexity, xAI)."""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": question},
                ],
                "max_tokens": _MAX_TOKENS,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _build(model: str, text: str, brand: str) -> AiResponse:
    mentioned, rank, snippet = _detect_mention(text, brand)
    return AiResponse(model=model, mentioned=mentioned, rank=rank, snippet=snippet)


# ── 엔진 레지스트리 ───────────────────────────────────────────

@dataclass(frozen=True)
class AiEngine:
    name: str
    label: str
    call: Callable[[str, str], Awaitable[AiResponse]]
    has_key: Callable[[], bool]


ENGINES: list[AiEngine] = [
    AiEngine("chatgpt",    "ChatGPT",    ask_chatgpt,    lambda: bool(settings.openai_api_key)),
    AiEngine("claude",     "Claude",     ask_claude,     lambda: bool(settings.anthropic_api_key)),
    AiEngine("gemini",     "Gemini",     ask_gemini,     lambda: bool(settings.gemini_api_key)),
    AiEngine("perplexity", "Perplexity", ask_perplexity, lambda: bool(settings.perplexity_api_key)),
    AiEngine("grok",       "Grok",       ask_grok,       lambda: bool(settings.xai_api_key)),
]


def active_engines() -> list[AiEngine]:
    return [e for e in ENGINES if e.has_key()]
