"""Tests for diagnostics: health scoring, checkers and the health monitor."""
from __future__ import annotations

from modules.self_healing_engine.config.constants import (
    CHECK_FAILED,
    CHECK_PASSED,
    CHECK_WARNING,
    HEALTH_CRITICAL,
    HEALTH_HEALTHY,
    HEALTH_UNHEALTHY,
)
from modules.self_healing_engine.diagnostics.checkers import CheckResult
from modules.self_healing_engine.diagnostics.health import compute_health_score
from modules.self_healing_engine.monitoring import HealthMonitor
from modules.self_healing_engine.tests.helpers import make_context


def _result(status: str) -> CheckResult:
    return CheckResult(kind="test", name="t", status=status, severity="info")


def test_health_score_all_passed() -> None:
    score = compute_health_score([_result(CHECK_PASSED), _result(CHECK_PASSED)])
    assert score.score == 100.0
    assert score.status == HEALTH_HEALTHY


def test_health_score_penalties() -> None:
    score = compute_health_score(
        [_result(CHECK_PASSED), _result(CHECK_WARNING), _result(CHECK_FAILED)]
    )
    assert score.score == 60.0  # 100 - 10 - 30
    assert score.warnings == 1
    assert score.failed == 1
    assert score.status == HEALTH_UNHEALTHY  # 60 >= 40 -> unhealthy


def test_health_score_clamped() -> None:
    score = compute_health_score([_result(CHECK_FAILED)] * 10)
    assert score.score == 0.0
    assert score.status == HEALTH_CRITICAL


def test_monitor_run_updates_state_and_publishes() -> None:
    ctx = make_context()
    monitor = HealthMonitor()
    score = monitor.run(ctx)

    assert score.score >= 0
    assert ctx.state.last_health_score == score.score
    assert ctx.state.health_status == score.status
    assert len(monitor.results()) == 4  # DEFAULT_CHECKERS
    assert monitor.last_score() is not None
    assert "health.changed" in [e.type for e in ctx.events.history()]


def test_monitor_deterministic_with_resolved_config(tmp_path) -> None:
    ctx = make_context(tmp_path)
    first = HealthMonitor().run(ctx)
    second = HealthMonitor().run(ctx)
    assert first.score == second.score
    assert first.status == second.status
