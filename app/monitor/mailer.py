"""Resend HTTP API로 메일을 보낸다.

기존 httpx를 쓰므로 신규 의존성이 없다. 키가 없으면 보내지 않고 로그만 남긴다 —
AI 엔진 미설정과 같은 처리라 로컬·CI에서 설정 없이도 안전하게 돌아간다.
"""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_ENDPOINT = "https://api.resend.com/emails"
_TIMEOUT = 20.0


class MailNotConfigured(RuntimeError):
    pass


def is_configured() -> bool:
    return bool(settings.resend_api_key and settings.resend_from)


async def send_email(
    *,
    to: str,
    subject: str,
    html_body: str,
    unsubscribe_url: str | None = None,
) -> None:
    """실패하면 예외를 던진다. 호출부가 성공한 발송만 기록하도록 하기 위함이다."""
    if not is_configured():
        raise MailNotConfigured("RESEND_API_KEY / RESEND_FROM 미설정")

    payload: dict = {
        "from": settings.resend_from,
        "to": [to],
        "subject": subject,
        "html": html_body,
    }
    if unsubscribe_url:
        # 도달률 요건. 메일 클라이언트가 자체 수신거부 버튼을 띄운다.
        payload["headers"] = {"List-Unsubscribe": f"<{unsubscribe_url}>"}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            _ENDPOINT,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json=payload,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Resend {resp.status_code}: {resp.text[:200]}")
