from __future__ import annotations

import pytest

from SuperDev.monitoring.health.health_checker import HealthChecker
from SuperDev.monitoring.health.component_health import ComponentHealth
from SuperDev.monitoring.health.dependency_health import DependencyHealth
from SuperDev.monitoring.health.health_aggregator import HealthAggregator
from SuperDev.monitoring.health.health_history import HealthHistory
from SuperDev.monitoring.health.health_notification import HealthNotification


class TestHealthChecker:
    def test_check(self) -> None:
        checker = HealthChecker()
        result = checker.check()
        assert result is not None


class TestComponentHealth:
    def test_healthy(self) -> None:
        h = ComponentHealth.healthy("cpu")
        assert h.status == "healthy"

    def test_unhealthy(self) -> None:
        h = ComponentHealth.unhealthy("cpu", "error")
        assert h.status == "unhealthy"


class TestDependencyHealth:
    def test_from_bool(self) -> None:
        h = DependencyHealth.from_bool("db", True)
        assert h.status == "healthy"
        h2 = DependencyHealth.from_bool("db", False)
        assert h2.status == "unhealthy"


class TestHealthAggregator:
    def test_aggregate(self) -> None:
        agg = HealthAggregator()
        agg.record_check("cpu", "healthy")
        assert agg.uptime > 0


class TestHealthHistory:
    def test_record_and_snapshot(self) -> None:
        h = HealthHistory()
        h.record("cpu", "healthy")
        snapshots = h.snapshots()
        assert len(snapshots) >= 1


class TestHealthNotification:
    def test_on_change(self) -> None:
        n = HealthNotification()
        calls: list[str] = []

        def cb(status: str) -> None:
            calls.append(status)

        n.on_change("cpu", cb)
        n.notify("cpu", "unhealthy")
        assert len(calls) == 1
