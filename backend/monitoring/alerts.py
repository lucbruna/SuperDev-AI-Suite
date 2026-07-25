from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from backend.utils.uuid_utils import generate_uuid


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Alert:
    id: str
    name: str
    message: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    source: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None


class AlertManager:
    """Alert management system."""

    def __init__(self):
        self._alerts: dict[str, Alert] = {}

    def create_alert(
        self,
        name: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        source: str = "",
        details: dict[str, Any] | None = None,
    ) -> Alert:
        alert = Alert(
            id=generate_uuid(),
            name=name,
            message=message,
            severity=severity,
            source=source,
            details=details or {},
        )
        self._alerts[alert.id] = alert
        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now(timezone.utc)
            return True
        return False

    def acknowledge_alert(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            return True
        return False

    def get_active_alerts(self) -> list[Alert]:
        return [a for a in self._alerts.values() if a.status == AlertStatus.ACTIVE]

    def get_all_alerts(self, limit: int = 100) -> list[Alert]:
        return sorted(self._alerts.values(), key=lambda a: a.created_at, reverse=True)[:limit]

    def delete_alert(self, alert_id: str) -> bool:
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            return True
        return False


alert_manager = AlertManager()
