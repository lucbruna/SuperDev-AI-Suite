"""Monitoring engine: facade over metrics, health, alerts, and audit."""

from __future__ import annotations

import logging
from typing import Any

from .alerting import AlertManager
from .audit import AuditLog
from .dashboard import MonitoringDashboard
from .health_check import HealthCheck
from .metrics_collector import MetricsCollector
from .telemetry import Telemetry


class MonitoringEngine:
    """Facade for the monitoring subsystem."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.monitoring")
        self.metrics = MetricsCollector()
        self.health = HealthCheck()
        self.alerts = AlertManager()
        self.audit = AuditLog()
        self.telemetry = Telemetry()
        self.dashboard = MonitoringDashboard(self.metrics, self.health, self.alerts)

    def probe(self, name: str, fn: Any) -> None:
        self.health.register(name, fn)

    def check(self, name: str | None = None) -> dict[str, str]:
        if name is None:
            return self.health.check_all()
        return {name: self.health.check(name)}

    def alert(self, name: str, severity: str = "warning",
              message: str = "") -> None:
        self.alerts.raise_alert(name, severity, message)

    def report(self) -> dict[str, Any]:
        return self.dashboard.render()
