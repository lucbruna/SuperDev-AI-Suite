"""Monitoring engine (Volume 37, Fase 4)."""

from __future__ import annotations

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (HealthCheckResult, HealthStatus,
                                         MetricSample, Severity)
from devops_engine.devops_protocols import new_id, now
from devops_engine.monitoring.alert_manager import Alert, AlertManager
from devops_engine.monitoring.anomaly_detector import AnomalyDetector
from devops_engine.monitoring.dashboard_manager import (Dashboard,
                                                        DashboardManager)
from devops_engine.monitoring.metric_store import MetricStore


class MonitoringEngine:
    """Facade over metrics, health checks, alerts and dashboards."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.metric_store = MetricStore()
        self.alerts = AlertManager()
        self.anomalies = AnomalyDetector()
        self.dashboards = DashboardManager()

    def record_metric(self, name: str, value: float, unit: str = "",
                      source: str = "") -> MetricSample:
        return self.metric_store.record(name, value, unit, source)

    def check(self, target: str,
              status: HealthStatus = HealthStatus.HEALTHY,
              latency_ms: float = 10.0) -> HealthCheckResult:
        result = HealthCheckResult(
            check_id=new_id("check"),
            target=target,
            status=status,
            latency_ms=latency_ms,
            checked_at=now(),
        )
        self.events.publish(DevopsEventType.HEALTH_CHECKED,
                            {"target": target, "status": status.value})
        if status == HealthStatus.UNHEALTHY:
            self.events.publish(DevopsEventType.HEALTH_DEGRADED,
                                {"target": target})
        return result

    def evaluate(self, name: str) -> Alert | None:
        """Runs anomaly detection over a metric's recent samples."""
        values = [sample.value
                  for sample in self.metric_store.get(name)]
        if not self.anomalies.detect(values):
            return None
        alert = self.raise_alert(
            f"Anomaly detected on {name}",
            severity=Severity.CRITICAL, source=name)
        self.events.publish(DevopsEventType.ANOMALY_DETECTED,
                            {"metric": name,
                             "value": values[-1] if values else 0.0})
        return alert

    def raise_alert(self, title: str,
                    severity: Severity = Severity.WARNING,
                    source: str = "") -> Alert:
        alert = self.alerts.raise_alert(title, severity, source)
        self.events.publish(DevopsEventType.ALERT_RAISED,
                            {"alert_id": alert.alert_id, "title": title})
        self.metrics.increment("devops.monitoring.alerts")
        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        if not self.alerts.resolve(alert_id):
            return False
        self.events.publish(DevopsEventType.ALERT_RESOLVED,
                            {"alert_id": alert_id})
        return True

    def create_dashboard(self, name: str,
                         metrics: list[str] | None = None) -> Dashboard:
        return self.dashboards.create(name, metrics)

    def stats(self) -> dict[str, int]:
        return {
            "samples": self.metric_store.count(),
            "alerts": self.alerts.count(),
            "dashboards": self.dashboards.count(),
        }
