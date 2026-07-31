"""Security monitoring engine."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class SecurityAlert:
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.INFO
    source: str = ""
    status: AlertStatus = AlertStatus.OPEN
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class MetricSnapshot:
    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MonitoringRule:
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    metric: str = ""
    threshold: float = 0.0
    operator: str = "gt"
    severity: AlertSeverity = AlertSeverity.WARNING
    enabled: bool = True


class MonitoringEngine:
    def __init__(self):
        self._alerts: Dict[str, SecurityAlert] = {}
        self._metrics: List[MetricSnapshot] = []
        self._rules: Dict[str, MonitoringRule] = {}
        self._max_metrics: int = 10000

    def record_metric(self, name: str, value: float, unit: str = "", tags: Optional[Dict[str, str]] = None) -> MetricSnapshot:
        snap = MetricSnapshot(metric_name=name, value=value, unit=unit, tags=tags or {})
        self._metrics.append(snap)
        if len(self._metrics) > self._max_metrics:
            self._metrics = self._metrics[-self._max_metrics:]
        self._evaluate_rules(name, value)
        return snap

    def add_rule(self, rule: MonitoringRule) -> None:
        self._rules[rule.rule_id] = rule

    def _evaluate_rules(self, metric_name: str, value: float) -> None:
        for rule in self._rules.values():
            if not rule.enabled or rule.metric != metric_name:
                continue
            triggered = False
            if rule.operator == "gt" and value > rule.threshold:
                triggered = True
            elif rule.operator == "lt" and value < rule.threshold:
                triggered = True
            elif rule.operator == "eq" and value == rule.threshold:
                triggered = True
            elif rule.operator == "gte" and value >= rule.threshold:
                triggered = True
            elif rule.operator == "lte" and value <= rule.threshold:
                triggered = True
            if triggered:
                alert = SecurityAlert(
                    title=f'Rule "{rule.name}" triggered',
                    description=f"{metric_name}={value} {rule.operator} {rule.threshold}",
                    severity=rule.severity,
                    source="monitoring_engine",
                )
                self._alerts[alert.alert_id] = alert

    def create_alert(self, title: str, description: str = "", severity: AlertSeverity = AlertSeverity.WARNING, source: str = "") -> SecurityAlert:
        alert = SecurityAlert(title=title, description=description, severity=severity, source=source)
        self._alerts[alert.alert_id] = alert
        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if not alert or alert.status != AlertStatus.OPEN:
            return False
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()
        return True

    def resolve_alert(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if not alert:
            return False
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        return True

    def get_alerts(self, severity: Optional[AlertSeverity] = None, status: Optional[AlertStatus] = None) -> List[SecurityAlert]:
        alerts = list(self._alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if status:
            alerts = [a for a in alerts if a.status == status]
        return alerts

    def get_metrics(self, name: Optional[str] = None, limit: int = 100) -> List[MetricSnapshot]:
        metrics = list(self._metrics)
        if name:
            metrics = [m for m in metrics if m.metric_name == name]
        return metrics[-limit:]

    def get_stats(self) -> dict:
        alerts = list(self._alerts.values())
        return {
            "total_alerts": len(alerts),
            "open": len([a for a in alerts if a.status == AlertStatus.OPEN]),
            "acknowledged": len([a for a in alerts if a.status == AlertStatus.ACKNOWLEDGED]),
            "resolved": len([a for a in alerts if a.status == AlertStatus.RESOLVED]),
            "critical": len([a for a in alerts if a.severity == AlertSeverity.CRITICAL]),
            "total_metrics": len(self._metrics),
            "rules": len(self._rules),
        }
