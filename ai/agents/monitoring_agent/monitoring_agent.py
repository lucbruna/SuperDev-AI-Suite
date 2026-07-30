from __future__ import annotations

from typing import Any

from .alert_manager import AlertManager
from .anomaly_detector import AnomalyDetector
from .dashboard_generator import DashboardGenerator
from .health_checks import HealthChecks
from .log_analysis import LogAnalysis
from .metrics_collector import MetricsCollector
from .sla_monitor import SLAMonitor
from .tracing import Tracing


class MonitoringEngine:
    """Central orchestrator for monitoring and observability workflows."""

    def __init__(self) -> None:
        self._metrics = MetricsCollector()
        self._tracing = Tracing()
        self._log_analysis = LogAnalysis()
        self._anomaly = AnomalyDetector()
        self._alerts = AlertManager()
        self._dashboard = DashboardGenerator()
        self._sla = SLAMonitor()
        self._health = HealthChecks()

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    @property
    def tracing(self) -> Tracing:
        return self._tracing

    @property
    def log_analysis(self) -> LogAnalysis:
        return self._log_analysis

    @property
    def anomaly(self) -> AnomalyDetector:
        return self._anomaly

    @property
    def alerts(self) -> AlertManager:
        return self._alerts

    @property
    def dashboard(self) -> DashboardGenerator:
        return self._dashboard

    @property
    def sla(self) -> SLAMonitor:
        return self._sla

    @property
    def health(self) -> HealthChecks:
        return self._health

    def run_monitoring(self, target: dict[str, Any]) -> dict[str, Any]:
        checks = self._health.run_checks()
        return {"status": "monitored", "checks_passed": sum(1 for c in checks if c["status"] == "healthy")}

    def get_status(self) -> dict[str, Any]:
        return {
            "metrics": self._metrics.metric_count,
            "spans": self._tracing.span_count,
            "log_entries": self._log_analysis.entry_count,
            "baselines": self._anomaly.baseline_count,
            "alert_rules": self._alerts.rule_count,
            "dashboard_panels": self._dashboard.panel_count,
            "slos": self._sla.slo_count,
            "health_checks": self._health.check_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "monitoring_agent", "status": self.get_status()}
