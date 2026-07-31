"""Monitoring dashboard: aggregates metrics, health, and alerts."""

from __future__ import annotations

from typing import Any

from .alerting import AlertManager
from .health_check import HealthCheck
from .metrics_collector import MetricsCollector


class MonitoringDashboard:
    """Composes a unified status view for the platform."""

    def __init__(self, metrics: MetricsCollector,
                 health: HealthCheck, alerts: AlertManager) -> None:
        self._metrics = metrics
        self._health = health
        self._alerts = alerts

    def render(self) -> dict[str, Any]:
        return {
            "status": self._health.overall(),
            "health": self._health.check_all(),
            "metrics": self._metrics.snapshot(),
            "alerts": {
                "total": self._alerts.count(),
                "critical": self._alerts.count("critical"),
                "warning": self._alerts.count("warning"),
                "active": self._alerts.active()[-5:],
            },
        }
