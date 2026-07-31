"""Alert management."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Alert:
    def __init__(self, title: str, severity: AlertSeverity, source: str = "", details: str = "") -> None:
        self.alert_id = str(uuid.uuid4())[:8]
        self.title = title
        self.severity = severity
        self.source = source
        self.details = details
        self.status = AlertStatus.OPEN
        self.created_at = time.time()
        self.acknowledged_at: float | None = None
        self.resolved_at: float | None = None


class AlertManager:
    def __init__(self) -> None:
        self._alerts: dict[str, Alert] = {}
        self._escalation_rules: list[dict[str, Any]] = []
        self._notification_handlers: dict[str, Callable[..., Any]] = {}

    def create_alert(self, title: str, severity: AlertSeverity, source: str = "", details: str = "") -> Alert:
        alert = Alert(title, severity, source, details)
        self._alerts[alert.alert_id] = alert
        self._check_escalation(alert)
        return alert

    def acknowledge(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert and alert.status == AlertStatus.OPEN:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = time.time()
            return True
        return False

    def resolve(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = time.time()
            return True
        return False

    def dismiss(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.DISMISSED
            return True
        return False

    def add_escalation_rule(self, severity: AlertSeverity, after_minutes: int, action: str) -> None:
        self._escalation_rules.append({"severity": severity.value, "after_minutes": after_minutes, "action": action})

    def register_notification(self, action: str, handler: Callable[..., Any]) -> None:
        self._notification_handlers[action] = handler

    def _check_escalation(self, alert: Alert) -> None:
        for rule in self._escalation_rules:
            if rule["severity"] == alert.severity.value:
                handler = self._notification_handlers.get(rule["action"])
                if handler:
                    handler(alert)

    def get_alerts(
        self, severity: AlertSeverity | None = None, status: AlertStatus | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        alerts = list(self._alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if status:
            alerts = [a for a in alerts if a.status == status]
        return [
            {
                "id": a.alert_id,
                "title": a.title,
                "severity": a.severity.value,
                "status": a.status.value,
                "source": a.source,
                "created_at": a.created_at,
            }
            for a in alerts[-limit:]
        ]

    def stats(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for alert in self._alerts.values():
            counts[alert.status.value] = counts.get(alert.status.value, 0) + 1
        return counts
