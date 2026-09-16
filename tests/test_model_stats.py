"""엔진별 집계 — 실패한 호출이 언급률을 오염시키지 않는지 확인한다.

실패를 분모에 넣으면 크레딧 소진이나 장애가 '0% 언급'으로 보여서,
실제로 AI가 추천하지 않은 것과 구분되지 않는다.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.orm import MonitorRun
from app.monitor.router import model_stats

_BASE = datetime(2026, 9, 16, 9, 0, tzinfo=timezone.utc)


def _run(model: str, mentioned: bool, *, error: str | None = None, rank: int | None = None, minutes: int = 0):
    return MonitorRun(
        question_id=1,
        ai_model=model,
        mentioned=mentioned,
        rank=rank,
        error=error,
        ran_at=_BASE + timedelta(minutes=minutes),
    )


def _by_name(stats):
    return {s.ai_model: s for s in stats}


def test_all_engines_present_even_without_runs():
    stats = model_stats([])
    assert {"chatgpt", "claude", "gemini", "perplexity", "grok"} <= set(_by_name(stats))


def test_failures_excluded_from_rate():
    """2번 성공(1번 언급) + 1번 실패 -> 50%, 33%가 아니다."""
    runs = [
        _run("chatgpt", True, rank=2),
        _run("chatgpt", False),
        _run("chatgpt", False, error="boom"),
    ]
    s = _by_name(model_stats(runs))["chatgpt"]
    assert s.total_runs == 2
    assert s.mentioned_runs == 1
    assert s.rate == 0.5
    assert s.failed_runs == 1


def test_only_failures_is_not_zero_percent_mention():
    """전부 실패했으면 성공 0건이므로 '측정된 언급률'이 존재하지 않는다."""
    runs = [_run("claude", False, error="credit too low")]
    s = _by_name(model_stats(runs))["claude"]
    assert s.total_runs == 0
    assert s.failed_runs == 1
    assert s.rate == 0.0
    assert s.last_error == "credit too low"


def test_last_error_is_most_recent():
    runs = [
        _run("claude", False, error="오래된 오류", minutes=0),
        _run("claude", False, error="최근 오류", minutes=30),
    ]
    assert _by_name(model_stats(runs))["claude"].last_error == "최근 오류"


def test_no_failures_leaves_error_fields_clean():
    runs = [_run("chatgpt", True, rank=1)]
    s = _by_name(model_stats(runs))["chatgpt"]
    assert s.failed_runs == 0
    assert s.last_error is None
    assert s.rate == 1.0


def test_avg_rank_ignores_failed_and_unmentioned():
    runs = [
        _run("chatgpt", True, rank=1),
        _run("chatgpt", True, rank=3),
        _run("chatgpt", False),
        _run("chatgpt", False, error="boom"),
    ]
    assert _by_name(model_stats(runs))["chatgpt"].avg_rank == 2.0
