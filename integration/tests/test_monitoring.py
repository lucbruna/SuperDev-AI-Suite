"""Tests for the monitoring subsystem (monitoring/)."""

from __future__ import annotations

from typing import Any

from integration.monitoring.alerting import AlertManager
from integration.monitoring.audit import AuditLog
from integration.monitoring.dashboard import MonitoringDashboard
from integration.monitoring.health_check import HealthCheck
from integration.monitoring.metrics_collector import MetricsCollector
from integration.monitoring.monitoring_engine import MonitoringEngine
from integration.monitoring.telemetry import Telemetry


class TestMetricsCollector:
    def test_counters_gauges(self) -> None:
        metrics = MetricsCollector()
        metrics.increment("requests")
        metrics.increment("requests")
        metrics.increment("errors")
        metrics.set_gauge("connections", 3)
        assert metrics.counter("requests") == 2
        assert metrics.counter("errors") == 1
        assert metrics.gauge("connections") == 3.0

    def test_timings(self) -> None:
        metrics = MetricsCollector()
        stop = metrics.timed("api.call")
        stop()
        assert metrics.average_timing("api.call") >= 0.0
        assert "avg_timings" in metrics.snapshot()

    def test_snapshot(self) -> None:
        metrics = MetricsCollector()
        metrics.increment("x")
        snapshot = metrics.snapshot()
        assert snapshot["counters"] == {"x": 1}


class TestHealthCheck:
    def test_probes(self) -> None:
        health = HealthCheck()
        health.register("erp", lambda: True)
        health.register("payments", lambda: False)
        assert health.check("erp") == "up"
        assert health.check("payments") == "down"
        assert health.overall() == "degraded"
        assert health.check_all() == {"erp": "up", "payments": "down"}

    def test_missing_and_exception(self) -> None:
        health = HealthCheck()
        assert health.check("missing") == "down"

        def boom() -> bool:
            raise RuntimeError("down")

        health.register("boom", boom)
        assert health.check("boom") == "down"

    def test_all_up(self) -> None:
        health = HealthCheck()
        health.register("a", lambda: True)
        health.register("b", lambda: True)
        assert health.overall() == "up"


class TestAlertManager:
    def test_raise_and_threshold(self) -> None:
        alerts = AlertManager()
        fired: list[dict[str, Any]] = []
        alerts.on_alert(lambda a: fired.append(a))
        alerts.raise_alert("high-latency", "critical", "p95 > 500ms")
        assert alerts.count("critical") == 1
        assert len(fired) == 1
        assert alerts.check_threshold("cpu", 90, 80) is True
        assert alerts.check_threshold("cpu", 50, 80) is False
        assert alerts.count() == 2

    def test_clear(self) -> None:
        alerts = AlertManager()
        alerts.raise_alert("x")
        alerts.clear()
        assert alerts.count() == 0


class TestAuditLog:
    def test_record_and_filter(self) -> None:
        audit = AuditLog()
        audit.record("alice", "connect", "erp")
        audit.record("alice", "sync", "fin")
        audit.record("bob", "connect", "pix")
        assert audit.count() == 3
        assert len(audit.filter(actor="alice")) == 2
        assert len(audit.filter(action="connect")) == 2
        assert len(audit.filter(actor="bob", action="sync")) == 0
        audit.clear()
        assert audit.count() == 0


class TestTelemetry:
    def test_events_and_failures(self) -> None:
        telemetry = Telemetry()
        telemetry.emit("connectors", "started")
        telemetry.emit("connectors", "failed", {"reason": "timeout"})
        telemetry.emit("events", "started")
        assert len(telemetry.events()) == 3
        assert len(telemetry.events(component="connectors")) == 2
        assert len(telemetry.failures()) == 1


class TestMonitoringDashboard:
    def test_render(self) -> None:
        metrics = MetricsCollector()
        health = HealthCheck()
        alerts = AlertManager()
        health.register("erp", lambda: True)
        metrics.increment("requests")
        dashboard = MonitoringDashboard(metrics, health, alerts)
        report = dashboard.render()
        assert report["status"] == "up"
        assert report["metrics"]["counters"] == {"requests": 1}
        assert report["alerts"]["total"] == 0


class TestMonitoringEngine:
    def test_end_to_end(self) -> None:
        engine = MonitoringEngine()
        engine.probe("erp", lambda: True)
        engine.probe("payments", lambda: False)
        assert engine.check() == {"erp": "up", "payments": "down"}
        engine.alert("payments-down", "critical", "payments offline")
        engine.audit.record("ops", "probe", "payments")
        engine.telemetry.emit("payments", "failed")
        report = engine.report()
        assert report["status"] == "degraded"
        assert report["alerts"]["critical"] == 1
        assert engine.audit.count() == 1
