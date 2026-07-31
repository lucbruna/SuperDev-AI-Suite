"""Alert management for integration monitoring."""

from __future__ import annotations

import time
from typing import Any, Callable


class AlertManager:
    """Raises and records alerts when thresholds are crossed."""

    def __init__(self) -> None:
        self._handlers: list[Callable[[dict[str, Any]], None]] = []
        self._alerts: list[dict[str, Any]] = []

    def on_alert(self, handler: Callable[[dict[str, Any]], None]) -> None:
        self._handlers.append(handler)

    def raise_alert(self, name: str, severity: str = "warning",
                    message: str = "") -> None:
        alert = {
            "name": name,
            "severity": severity,
            "message": message,
            "timestamp": time.time(),
        }
        self._alerts.append(alert)
        for handler in self._handlers:
            handler(alert)

    def check_threshold(self, name: str, value: float, max_value: float,
                        severity: str = "warning") -> bool:
        if value > max_value:
            self.raise_alert(name, severity, f"{value:.2f} > {max_value:.2f}")
            return True
        return False

    def active(self) -> list[dict[str, Any]]:
        return list(self._alerts)

    def count(self, severity: str | None = None) -> int:
        if severity is None:
            return len(self._alerts)
        return sum(1 for a in self._alerts if a["severity"] == severity)

    def clear(self) -> None:
        self._alerts.clear()
