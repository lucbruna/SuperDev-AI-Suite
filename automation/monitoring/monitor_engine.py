"""Monitor engine: facade for the monitoring subsystem.

Implements the core ``Monitor`` interface (``report()``).
"""

from __future__ import annotations

import time
from typing import Any, Callable

from automation.automation_interfaces import Monitor
from automation.monitoring.monitor_alert import MonitorAlerting
from automation.monitoring.monitor_checker import MonitorChecker
from automation.monitoring.monitor_history import MonitorHistory
from automation.monitoring.monitor_models import MonitorCheck, MonitorStatus


class MonitorEngine(Monitor):
    """Tracks and reports on automation health."""

    def __init__(self, checker: MonitorChecker | None = None,
                 alerting: MonitorAlerting | None = None,
                 history: MonitorHistory | None = None,
                 enabled: bool = True) -> None:
        self.checker = checker or MonitorChecker()
        self.alerting = alerting or MonitorAlerting()
        self.history = history or MonitorHistory()
        self.enabled = enabled
        self._last: list[MonitorCheck] = []

    def register_check(self, check_id: str, name: str,
                       probe: Callable[[], bool | tuple[bool, str]]) -> None:
        self.checker.register(check_id, name, probe)

    def run(self, check_id: str | None = None) -> list[MonitorCheck]:
        """Runs one check (or all when check_id is None)."""
        if not self.enabled:
            return []
        if check_id is None:
            checks = self.checker.run_all()
        else:
            check = self.checker.run(check_id)
            checks = [check] if check is not None else []
        for check in checks:
            self.alerting.notify(check)
        self._last = checks
        return checks

    def status(self) -> str:
        if not self.enabled:
            return "disabled"
        if not self._last:
            return "unknown"
        if any(c.status is MonitorStatus.CRITICAL for c in self._last):
            return "critical"
        if any(c.status is MonitorStatus.WARNING for c in self._last):
            return "warning"
        return "healthy"

    def recent_alerts(self, limit: int = 10) -> list[dict[str, Any]]:
        return [a.to_dict() for a in self.alerting.recent(limit)]

    def report(self) -> dict[str, Any]:
        """Implements Monitor.report() — snapshot of the current state."""
        if not self.enabled:
            data = {"status": "disabled", "checks": [],
                    "alerts": [], "timestamp": time.time()}
            self.history.snapshot(data)
            return data
        if not self._last:
            self.run()
        data = {
            "status": self.status(),
            "total": len(self._last),
            "healthy": sum(1 for c in self._last
                           if c.status is MonitorStatus.HEALTHY),
            "warning": sum(1 for c in self._last
                           if c.status is MonitorStatus.WARNING),
            "critical": sum(1 for c in self._last
                            if c.status is MonitorStatus.CRITICAL),
            "checks": [c.to_dict() for c in self._last],
            "alerts": self.recent_alerts(10),
            "timestamp": time.time(),
        }
        self.history.snapshot(data)
        return data
