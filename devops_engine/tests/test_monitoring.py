"""Tests for the monitoring subpackage (Volume 37, Fase 4)."""

from __future__ import annotations

import pytest

from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import (HealthStatus, Severity)
from devops_engine.monitoring import Alert, MonitoringEngine


@pytest.fixture()
def monitoring() -> MonitoringEngine:
    return MonitoringEngine()


class TestMetricStore:
    def test_record_and_get(self, monitoring: MonitoringEngine) -> None:
        monitoring.record_metric("cpu", 0.5, unit="percent")
        samples = monitoring.metric_store.get("cpu")
        assert len(samples) == 1
        assert samples[0].unit == "percent"

    def test_aggregates(self, monitoring: MonitoringEngine) -> None:
        for value in (1.0, 2.0, 3.0):
            monitoring.record_metric("latency", value)
        assert monitoring.metric_store.avg("latency") == 2.0
        assert monitoring.metric_store.max("latency") == 3.0
        last = monitoring.metric_store.last("latency")
        assert last is not None
        assert last.value == 3.0
        assert monitoring.metric_store.count() == 3


class TestAnomalyDetector:
    def test_flat_series_no_anomaly(self, monitoring: MonitoringEngine) -> None:
        for _ in range(10):
            monitoring.record_metric("cpu", 0.4)
        assert monitoring.evaluate("cpu") is None

    def test_spike_is_anomaly(self, monitoring: MonitoringEngine) -> None:
        for _ in range(10):
            monitoring.record_metric("cpu", 0.4)
        monitoring.record_metric("cpu", 9.9)
        alert = monitoring.evaluate("cpu")
        assert alert is not None
        assert alert.severity == Severity.CRITICAL

    def test_short_series_no_anomaly(self, monitoring: MonitoringEngine) -> None:
        monitoring.record_metric("cpu", 0.4)
        assert monitoring.evaluate("cpu") is None


class TestAlertManager:
    def test_raise_resolve(self, monitoring: MonitoringEngine) -> None:
        alert = monitoring.alerts.raise_alert("high cpu")
        assert alert.status == "open"
        assert monitoring.alerts.resolve(alert.alert_id) is True
        assert alert.status == "resolved"

    def test_list_open(self, monitoring: MonitoringEngine) -> None:
        monitoring.alerts.raise_alert("a")
        monitoring.alerts.raise_alert("b")
        assert len(monitoring.alerts.list_open()) == 2


class TestDashboardManager:
    def test_create_list(self, monitoring: MonitoringEngine) -> None:
        dashboard = monitoring.create_dashboard("overview", ["cpu", "mem"])
        assert dashboard.metrics == ["cpu", "mem"]
        assert monitoring.dashboards.count() == 1


class TestMonitoringEngine:
    def test_check_events(self, monitoring: MonitoringEngine) -> None:
        events = DevopsEvents()
        monitoring.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.HEALTH_CHECKED, seen.append)
        result = monitoring.check("api", latency_ms=22.0)
        assert result.status == HealthStatus.HEALTHY
        assert result.latency_ms == 22.0
        assert len(seen) == 1

    def test_unhealthy_emits_degraded(self, monitoring: MonitoringEngine) -> None:
        events = DevopsEvents()
        monitoring.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.HEALTH_DEGRADED, seen.append)
        result = monitoring.check("api", status=HealthStatus.UNHEALTHY)
        assert result.status == HealthStatus.UNHEALTHY
        assert len(seen) == 1

    def test_raise_alert_event(self, monitoring: MonitoringEngine) -> None:
        events = DevopsEvents()
        monitoring.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.ALERT_RAISED, seen.append)
        alert = monitoring.raise_alert("disk full", Severity.WARNING)
        assert isinstance(alert, Alert)
        assert len(seen) == 1
        assert monitoring.metrics.count("devops.monitoring.alerts") == 1

    def test_resolve_alert_event(self, monitoring: MonitoringEngine) -> None:
        alert = monitoring.raise_alert("disk full")
        events = DevopsEvents()
        monitoring.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.ALERT_RESOLVED, seen.append)
        assert monitoring.resolve_alert(alert.alert_id) is True
        assert len(seen) == 1

    def test_anomaly_event(self, monitoring: MonitoringEngine) -> None:
        events = DevopsEvents()
        monitoring.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.ANOMALY_DETECTED, seen.append)
        for _ in range(10):
            monitoring.record_metric("cpu", 0.4)
        monitoring.record_metric("cpu", 9.9)
        assert monitoring.evaluate("cpu") is not None
        assert len(seen) == 1

    def test_stats(self, monitoring: MonitoringEngine) -> None:
        monitoring.record_metric("cpu", 0.4)
        monitoring.raise_alert("x")
        monitoring.create_dashboard("overview")
        stats = monitoring.stats()
        assert stats["samples"] == 1
        assert stats["alerts"] == 1
        assert stats["dashboards"] == 1
