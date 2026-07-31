"""Alert management for monitoring (Volume 37, Fase 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from devops_engine.devops_models import Severity
from devops_engine.devops_protocols import new_id, now


@dataclass
class Alert:
    """A raised monitoring alert."""
    alert_id: str
    title: str
    severity: Severity = Severity.WARNING
    status: str = "open"
    source: str = ""
    created_at: float = 0.0
    resolved_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class AlertManager:
    """Raises, lists and resolves alerts."""

    def __init__(self) -> None:
        self._alerts: dict[str, Alert] = {}

    def raise_alert(self, title: str,
                    severity: Severity = Severity.WARNING,
                    source: str = "") -> Alert:
        alert = Alert(
            alert_id=new_id("alert"),
            title=title,
            severity=severity,
            status="open",
            source=source,
            created_at=now(),
        )
        self._alerts[alert.alert_id] = alert
        return alert

    def resolve(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert is None:
            return False
        alert.status = "resolved"
        alert.resolved_at = now()
        return True

    def get(self, alert_id: str) -> Alert | None:
        return self._alerts.get(alert_id)

    def list_open(self) -> list[Alert]:
        return [alert for alert in self._alerts.values()
                if alert.status == "open"]

    def count(self) -> int:
        return len(self._alerts)
