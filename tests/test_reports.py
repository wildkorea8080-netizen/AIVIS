"""주간 리포트 — 보낼지 말지의 판단과 이스케이프를 고정한다.

가장 위험한 실수는 데이터가 없는 주에 "0%"를 보내는 것이다. 브랜드가 모든 AI에서
사라진 것처럼 읽히지만 실제 원인은 우리 쪽 실행이 안 돈 것이다.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.models.orm import MonitorMention, MonitorProject, MonitorRun
from app.monitor.reports import (
    MIN_RUNS_TO_SEND,
    build_weekly_report,
    render_html,
    render_subject,
)

_NOW = datetime(2026, 9, 20, 9, 0, tzinfo=timezone.utc)
_BASE_URL = "https://aivis-iota.vercel.app"


def _project(name: str = "ACID", keyword: str = "어나더캠퍼") -> MonitorProject:
    return MonitorProject(
        id=1,
        owner_token="tok-123",
        name=name,
        target_url="https://acidhaus.kr/",
        mode="brand",
        brand_keyword=keyword,
    )


def _run(run_id: int, *, mentioned: bool, model: str = "chatgpt",
         error: str | None = None, days_ago: int = 1) -> MonitorRun:
    return MonitorRun(
        id=run_id,
        question_id=1,
        ai_model=model,
        mentioned=mentioned,
        error=error,
        ran_at=_NOW - timedelta(days=days_ago),
    )


def _build(runs, mentions=None, project=None):
    return build_weekly_report(
        project or _project(),
        runs,
        mentions or {},
        now=_NOW,
        base_url=_BASE_URL,
    )


# ── 보낼지 말지 ────────────────────────────────────────────────

def test_no_runs_produces_no_report():
    assert _build([]) is None


def test_below_minimum_sample_is_not_sent():
    runs = [_run(i, mentioned=False) for i in range(MIN_RUNS_TO_SEND - 1)]
    assert _build(runs) is None


def test_failures_do_not_count_toward_the_minimum():
    """실패만 잔뜩 쌓인 주는 데이터가 있는 게 아니다."""
    runs = [_run(i, mentioned=False, error="boom") for i in range(10)]
    assert _build(runs) is None


def test_runs_outside_the_window_are_ignored():
    runs = [_run(i, mentioned=True, days_ago=30) for i in range(10)]
    assert _build(runs) is None


def test_enough_runs_produces_a_report():
    runs = [_run(i, mentioned=i < 2) for i in range(MIN_RUNS_TO_SEND)]
    report = _build(runs)
    assert report is not None
    assert report.total_runs == MIN_RUNS_TO_SEND
    assert report.mentioned_runs == 2


# ── 언급률 — 대시보드와 같은 분모 규칙 ─────────────────────────

def test_failed_runs_excluded_from_rate():
    runs = [_run(i, mentioned=i < 3) for i in range(6)]
    runs += [_run(99 + i, mentioned=False, error="boom") for i in range(4)]
    report = _build(runs)
    assert report.total_runs == 6          # 실패 4건 제외
    assert report.mention_rate == 0.5      # 3/6, 3/10이 아니다
    assert report.failed_runs == 4


def test_weakest_engine_is_the_lowest_rate():
    runs = [_run(i, mentioned=True, model="chatgpt") for i in range(3)]
    runs += [_run(10 + i, mentioned=False, model="claude") for i in range(3)]
    assert _build(runs).weakest_engine == "claude"


def test_weakest_engine_is_none_with_a_single_engine():
    runs = [_run(i, mentioned=False) for i in range(MIN_RUNS_TO_SEND)]
    assert _build(runs).weakest_engine is None


# ── 경쟁사 ─────────────────────────────────────────────────────

def test_competitors_ranked_and_own_brand_flagged():
    runs = [_run(i, mentioned=True) for i in range(MIN_RUNS_TO_SEND)]
    mentions = {
        0: [MonitorMention(run_id=0, name_raw="코베아", name_key="코베아", rank=1),
            MonitorMention(run_id=0, name_raw="어나더캠퍼", name_key="어나더캠퍼", rank=2)],
        1: [MonitorMention(run_id=1, name_raw="코베아", name_key="코베아", rank=1)],
    }
    report = _build(runs, mentions)
    assert [c.name for c in report.competitors] == ["코베아", "어나더캠퍼"]
    assert report.competitors[0].mentions == 2
    assert report.competitors[0].is_own is False
    assert report.competitors[1].is_own is True


def test_mentions_on_failed_runs_are_ignored():
    runs = [_run(i, mentioned=False) for i in range(MIN_RUNS_TO_SEND)]
    runs.append(_run(77, mentioned=False, error="boom"))
    mentions = {77: [MonitorMention(run_id=77, name_raw="유령업체", name_key="유령업체", rank=1)]}
    assert _build(runs, mentions).competitors == []


# ── 렌더링 ─────────────────────────────────────────────────────

def test_html_escapes_untrusted_names():
    """경쟁사명은 AI 응답에서, 프로젝트명은 사용자 입력에서 온다."""
    runs = [_run(i, mentioned=True) for i in range(MIN_RUNS_TO_SEND)]
    mentions = {
        0: [MonitorMention(run_id=0, name_raw="<script>alert(1)</script>",
                           name_key="script", rank=1)]
    }
    report = _build(runs, mentions, project=_project(name="A & B <b>"))
    out = render_html(report)
    assert "<script>alert(1)</script>" not in out
    assert "&lt;script&gt;" in out
    assert "A &amp; B &lt;b&gt;" in out


def test_html_includes_dashboard_and_unsubscribe_links():
    runs = [_run(i, mentioned=True) for i in range(MIN_RUNS_TO_SEND)]
    out = render_html(_build(runs))
    assert f"{_BASE_URL}/monitor/tok-123" in out
    assert f"{_BASE_URL}/monitor/tok-123/unsubscribe" in out


@pytest.mark.parametrize("mentioned_count,expected", [(0, "등장하지 않았습니다"), (3, "언급률")])
def test_subject_reflects_whether_brand_appeared(mentioned_count, expected):
    runs = [_run(i, mentioned=i < mentioned_count) for i in range(6)]
    assert expected in render_subject(_build(runs))
