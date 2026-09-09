from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.monitor.router import RUN_COOLDOWN, cooldown_remaining

_NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)


def test_never_run_is_allowed():
    assert cooldown_remaining(None, _NOW) is None


def test_just_ran_is_blocked():
    remaining = cooldown_remaining(_NOW - timedelta(minutes=1), _NOW)
    assert remaining == RUN_COOLDOWN - timedelta(minutes=1)


def test_exactly_at_cooldown_is_allowed():
    assert cooldown_remaining(_NOW - RUN_COOLDOWN, _NOW) is None


def test_long_ago_is_allowed():
    assert cooldown_remaining(_NOW - timedelta(days=1), _NOW) is None


@pytest.mark.parametrize("minutes", [0, 1, 5, 9])
def test_within_window_blocked(minutes):
    assert cooldown_remaining(_NOW - timedelta(minutes=minutes), _NOW) is not None
