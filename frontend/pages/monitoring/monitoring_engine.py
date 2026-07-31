from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class MonitoringEngine:
    """Renders the monitoring page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.monitoring")
        self._context = context or FrontendContext()
        self._alerts: list[dict[str, Any]] = []

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "monitoring",
            "alerts": self.list_alerts(),
            "uptime": self.uptime(),
        }

    def list_alerts(self) -> list[dict[str, Any]]:
        return list(self._alerts)

    def raise_alert(self, severity: str, message: str) -> str:
        alert_id = f"alert-{len(self._alerts) + 1}"
        self._alerts.append(
            {"alert_id": alert_id, "severity": severity, "message": message, "ts": time.time()}
        )
        return alert_id

    def acknowledge(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                return True
        return False

    def uptime(self) -> dict[str, Any]:
        return {"percent": 99.98, "current": "operational"}
