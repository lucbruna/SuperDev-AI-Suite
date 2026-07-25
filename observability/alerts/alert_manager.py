import uuid
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Alert:
    id: str
    name: str
    severity: str  # critical, warning, info
    message: str
    status: str  # active, acknowledged, resolved
    timestamp: float
    acknowledged_at: Optional[float] = None
    resolved_at: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


class AlertManager:
    def __init__(self) -> None:
        self._alerts: Dict[str, Alert] = {}

    def trigger(self, alert_dict: Dict[str, Any]) -> Alert:
        alert_id = str(uuid.uuid4())
        alert = Alert(
            id=alert_id,
            name=alert_dict.get("name", "unknown"),
            severity=alert_dict.get("severity", "info"),
            message=alert_dict.get("message", ""),
            status="active",
            timestamp=time.time(),
            details=alert_dict.get("details", {}),
        )
        self._alerts[alert_id] = alert
        return alert

    def acknowledge(self, alert_id: str) -> Optional[Alert]:
        alert = self._alerts.get(alert_id)
        if alert is None:
            return None
        alert.status = "acknowledged"
        alert.acknowledged_at = time.time()
        return alert

    def resolve(self, alert_id: str) -> Optional[Alert]:
        alert = self._alerts.get(alert_id)
        if alert is None:
            return None
        alert.status = "resolved"
        alert.resolved_at = time.time()
        return alert

    def get_active(self) -> List[Alert]:
        return [a for a in self._alerts.values() if a.status in ("active", "acknowledged")]

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Alert]:
        results = list(self._alerts.values())
        if filters:
            for key, value in filters.items():
                results = [a for a in results if getattr(a, key, None) == value]
        return results

    def get(self, alert_id: str) -> Optional[Alert]:
        return self._alerts.get(alert_id)
