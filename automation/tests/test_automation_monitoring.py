"""Tests for the monitoring subsystem (Volume 20, Fase 7)."""

from __future__ import annotations

from automation.monitoring.monitor_alert import MonitorAlerting
from automation.monitoring.monitor_checker import MonitorChecker
from automation.monitoring.monitor_engine import MonitorEngine
from automation.monitoring.monitor_history import MonitorHistory
from automation.monitoring.monitor_models import (
    MonitorAlert,
    MonitorCheck,
    MonitorStatus,
)


class TestMonitorModels:
    def test_status_values(self) -> None:
        assert MonitorStatus.HEALTHY.value == "healthy"
        assert MonitorStatus.CRITICAL.value == "critical"

    def test_check_to_dict(self) -> None:
        check = MonitorCheck("c-1", "ERP", MonitorStatus.HEALTHY)
        data = check.to_dict()
        assert data["check_id"] == "c-1"
        assert data["status"] == "healthy"

    def test_alert_to_dict(self) -> None:
        alert = MonitorAlert("a-1", "c-1", "critical", "down")
        assert alert.to_dict()["level"] == "critical"


class TestMonitorChecker:
    def test_healthy_and_critical(self) -> None:
        checker = MonitorChecker()
        checker.register("erp", "ERP online", lambda: True)
        checker.register("api", "API online", lambda: False)
        checker.register("db", "Banco de dados",
                         lambda: (True, "latência 12ms"))
        checks = {c.check_id: c for c in checker.run_all()}
        assert checks["erp"].status is MonitorStatus.HEALTHY
        assert checks["api"].status is MonitorStatus.CRITICAL
        assert checks["db"].status is MonitorStatus.HEALTHY
        assert checks["db"].detail == "latência 12ms"
        assert set(checker.ids()) == {"erp", "api", "db"}

    def test_probe_exception_is_critical(self) -> None:
        checker = MonitorChecker()

        def boom() -> bool:
            raise ConnectionError("timeout")

        checker.register("x", "X", boom)
        check = checker.run("x")
        assert check is not None
        assert check.status is MonitorStatus.CRITICAL
        assert "timeout" in check.detail

    def test_unknown_check(self) -> None:
        assert MonitorChecker().run("ghost") is None


class TestMonitorAlerting:
    def test_no_alert_when_healthy(self) -> None:
        alerting = MonitorAlerting()
        check = MonitorCheck("c-1", "OK", MonitorStatus.HEALTHY)
        assert alerting.notify(check) is None
        assert alerting.count() == 0

    def test_alert_levels_and_count(self) -> None:
        alerting = MonitorAlerting()
        alerting.notify(MonitorCheck("c-1", "A", MonitorStatus.CRITICAL))
        alerting.notify(MonitorCheck("c-2", "B", MonitorStatus.WARNING))
        assert alerting.count() == 2
        assert alerting.count("critical") == 1
        assert alerting.count("warning") == 1

    def test_listener_notified(self) -> None:
        alerting = MonitorAlerting()
        seen: list[MonitorAlert] = []
        alerting.on_alert(lambda a: seen.append(a))
        alert = alerting.notify(MonitorCheck("c-1", "A", MonitorStatus.CRITICAL))
        assert alert is not None
        assert seen == [alert]

    def test_recent_limit(self) -> None:
        alerting = MonitorAlerting()
        for index in range(5):
            alerting.notify(MonitorCheck(f"c-{index}", str(index),
                                         MonitorStatus.CRITICAL))
        assert len(alerting.recent(2)) == 2
        assert alerting.recent(2)[-1].check_id == "c-4"


class TestMonitorEngine:
    def _engine(self) -> MonitorEngine:
        engine = MonitorEngine()
        engine.register_check("erp", "ERP online", lambda: True)
        engine.register_check("api", "API online", lambda: False)
        return engine

    def test_run_all_and_status(self) -> None:
        engine = self._engine()
        checks = engine.run()
        assert len(checks) == 2
        assert engine.status() == "critical"

    def test_run_single_check(self) -> None:
        engine = self._engine()
        checks = engine.run("erp")
        assert len(checks) == 1
        assert checks[0].check_id == "erp"
        assert engine.status() == "healthy"

    def test_healthy_status(self) -> None:
        engine = MonitorEngine()
        engine.register_check("ok", "OK", lambda: True)
        engine.run()
        assert engine.status() == "healthy"

    def test_report_implements_core_monitor_interface(self) -> None:
        from automation.automation_interfaces import Monitor
        engine = self._engine()
        assert isinstance(engine, Monitor)
        engine.run()
        report = engine.report()
        assert report["status"] == "critical"
        assert report["total"] == 2
        assert report["healthy"] == 1
        assert report["critical"] == 1
        assert len(report["alerts"]) == 1
        assert len(report["checks"]) == 2
        assert engine.history.count() >= 1

    def test_disabled_engine(self) -> None:
        engine = MonitorEngine(enabled=False)
        engine.register_check("x", "X", lambda: False)
        assert engine.run() == []
        assert engine.status() == "disabled"
        assert engine.report()["status"] == "disabled"

    def test_recent_alerts(self) -> None:
        engine = self._engine()
        engine.run()
        alerts = engine.recent_alerts()
        assert len(alerts) == 1
        assert alerts[0]["check_id"] == "api"


class TestMonitorHistory:
    def test_snapshot_list_count(self) -> None:
        history = MonitorHistory()
        history.snapshot({"status": "healthy"})
        history.snapshot({"status": "critical"})
        assert history.count() == 2
        assert history.list(1)[0]["status"] == "critical"
        history.clear()
        assert history.count() == 0
