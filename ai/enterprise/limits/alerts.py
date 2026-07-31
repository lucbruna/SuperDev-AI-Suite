"""Limit alerts."""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any


class LimitAlerts:
    def __init__(self) -> None:
        self._thresholds: dict[str, dict[str, float]] = {}
        self._handlers: dict[str, Callable] = {}
        self._alerts: list[dict[str, Any]] = []

    def set_threshold(self, resource: str, warning: float = 80.0, critical: float = 95.0) -> None:
        self._thresholds[resource] = {"warning": warning, "critical": critical}

    def set_handler(self, resource: str, handler: Callable) -> None:
        self._handlers[resource] = handler

    def check(self, org_id: str, resource: str, usage_percent: float) -> str:
        threshold = self._thresholds.get(resource, {"warning": 80, "critical": 95})
        if usage_percent >= threshold["critical"]:
            alert = {"org_id": org_id, "resource": resource, "level": "critical", "percent": usage_percent}
            self._alerts.append(alert)
            handler = self._handlers.get(resource)
            if handler:
                with contextlib.suppress(Exception):
                    handler(alert)
            return "critical"
        if usage_percent >= threshold["warning"]:
            alert = {"org_id": org_id, "resource": resource, "level": "warning", "percent": usage_percent}
            self._alerts.append(alert)
            return "warning"
        return "ok"

    def get_alerts(
        self, org_id: str = "", resource: str = "", level: str = "", limit: int = 50
    ) -> list[dict[str, Any]]:
        results = self._alerts
        if org_id:
            results = [a for a in results if a["org_id"] == org_id]
        if resource:
            results = [a for a in results if a["resource"] == resource]
        if level:
            results = [a for a in results if a["level"] == level]
        return results[-limit:]

    def list_thresholds(self) -> dict[str, dict[str, float]]:
        return dict(self._thresholds)

    def clear_alerts(self) -> int:
        n = len(self._alerts)
        self._alerts.clear()
        return n
