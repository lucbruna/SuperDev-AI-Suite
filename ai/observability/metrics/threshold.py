"""Metrics thresholds."""

from __future__ import annotations

from typing import Any


class Threshold:
    def __init__(self, name: str, warning: float = 0, critical: float = 0) -> None:
        self.name = name
        self.warning = warning
        self.critical = critical
        self.breached = False

    def check(self, value: float) -> str:
        if value >= self.critical:
            self.breached = True
            return "critical"
        if value >= self.warning:
            self.breached = True
            return "warning"
        self.breached = False
        return "ok"


class MetricsThresholdManager:
    def __init__(self) -> None:
        self._thresholds: dict[str, Threshold] = {}
        self._violations: list[dict[str, Any]] = []

    def add_threshold(self, name: str, warning: float, critical: float) -> None:
        self._thresholds[name] = Threshold(name, warning, critical)

    def remove_threshold(self, name: str) -> bool:
        if name in self._thresholds:
            del self._thresholds[name]
            return True
        return False

    def check(self, name: str, value: float) -> str:
        t = self._thresholds.get(name)
        if not t:
            return "no_threshold"
        status = t.check(value)
        if status != "ok":
            self._violations.append({"name": name, "value": value, "status": status})
        return status

    def get_violations(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._violations[-limit:]

    def list_thresholds(self) -> list[dict[str, Any]]:
        return [
            {"name": t.name, "warning": t.warning, "critical": t.critical, "breached": t.breached}
            for t in self._thresholds.values()
        ]
