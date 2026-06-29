"""AI 모델별 질문 호출 + 브랜드 언급 여부 판정."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.config import settings


@dataclass
class AiResponse:
    model: str          # chatgpt | claude | perplexity
    mentioned: bool
    rank: int | None    # 몇 번째 추천으로 언급됐는지 (1-based), 없으면 None
    snippet: str | None # 언급된 문장 발췌


def _detect_mention(text: str, brand: str) -> tuple[bool, int | None, str | None]:
    """응답 텍스트에서 브랜드 언급 여부와 순위를 판정."""
    lower_text = text.lower()
    lower_brand = brand.lower()

    if lower_brand not in lower_text:
        return False, None, None

    # 언급된 문장 추출
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


async def ask_chatgpt(question: str, brand: str) -> AiResponse:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY 미설정")

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 한국 소비자에게 비즈니스·서비스를 추천하는 AI 어시스턴트입니다. 질문에 구체적인 이름을 들어 추천해주세요."},
            {"role": "user", "content": question},
        ],
        max_tokens=800,
        temperature=0.3,
    )
    text = resp.choices[0].message.content or ""
    mentioned, rank, snippet = _detect_mention(text, brand)
    return AiResponse(model="chatgpt", mentioned=mentioned, rank=rank, snippet=snippet)


async def ask_claude(question: str, brand: str) -> AiResponse:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 미설정")

    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    resp = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        system="당신은 한국 소비자에게 비즈니스·서비스를 추천하는 AI 어시스턴트입니다. 질문에 구체적인 이름을 들어 추천해주세요.",
        messages=[{"role": "user", "content": question}],
    )
    text = resp.content[0].text if resp.content else ""
    mentioned, rank, snippet = _detect_mention(text, brand)
    return AiResponse(model="claude", mentioned=mentioned, rank=rank, snippet=snippet)


async def ask_perplexity(question: str, brand: str) -> AiResponse:
    if not settings.perplexity_api_key:
        raise RuntimeError("PERPLEXITY_API_KEY 미설정")

    import httpx
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {settings.perplexity_api_key}"},
            json={
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [{"role": "user", "content": question}],
            },
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]

    mentioned, rank, snippet = _detect_mention(text, brand)
    return AiResponse(model="perplexity", mentioned=mentioned, rank=rank, snippet=snippet)


# 사용 가능한 caller 목록 (키 있는 것만 실행)
ALL_CALLERS = [
    ("chatgpt", ask_chatgpt, lambda: bool(settings.openai_api_key)),
    ("claude", ask_claude, lambda: bool(settings.anthropic_api_key)),
    ("perplexity", ask_perplexity, lambda: bool(settings.perplexity_api_key)),
]
