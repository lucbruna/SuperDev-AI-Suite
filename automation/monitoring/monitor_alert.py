"""Alerting for failing health checks."""

from __future__ import annotations

import time
from typing import Any, Callable

from automation.automation_protocols import new_id
from automation.monitoring.monitor_models import (
    MonitorAlert,
    MonitorCheck,
    MonitorStatus,
)


class MonitorAlerting:
    """Turns unhealthy checks into alerts and notifies listeners."""

    def __init__(self) -> None:
        self._listeners: list[Callable[[MonitorAlert], None]] = []
        self._alerts: list[MonitorAlert] = []

    def on_alert(self, listener: Callable[[MonitorAlert], None]) -> None:
        self._listeners.append(listener)

    def notify(self, check: MonitorCheck) -> MonitorAlert | None:
        if check.status is MonitorStatus.HEALTHY:
            return None
        level = ("critical" if check.status is MonitorStatus.CRITICAL
                 else "warning")
        alert = MonitorAlert(
            alert_id=new_id("alert"),
            check_id=check.check_id,
            level=level,
            message=f"check '{check.check_id}' is {check.status.value}: "
                    f"{check.detail}",
            timestamp=time.time())
        self._alerts.append(alert)
        for listener in self._listeners:
            try:
                listener(alert)
            except Exception:  # noqa: BLE001
                pass
        return alert

    def recent(self, limit: int = 10) -> list[MonitorAlert]:
        return list(self._alerts[-limit:])

    def count(self, level: str | None = None) -> int:
        if level is None:
            return len(self._alerts)
        return sum(1 for a in self._alerts if a.level == level)
