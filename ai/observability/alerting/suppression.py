"""Alert suppression."""
from __future__ import annotations

import time
from typing import Any


class AlertSuppression:
    def __init__(self) -> None:
        self._suppressions: list[dict[str, Any]] = []
    def suppress(self, alert_type: str, duration_seconds: int = 300, reason: str = "") -> dict[str, Any]:
        entry = {"type": alert_type, "duration": duration_seconds, "reason": reason, "start_time": time.time(), "end_time": time.time() + duration_seconds}
        self._suppressions.append(entry)
        return entry
    def is_suppressed(self, alert_type: str) -> bool:
        now = time.time()
        return any(s["type"] == alert_type and s["end_time"] > now for s in self._suppressions)
    def unsuppress(self, alert_type: str) -> bool:
        before = len(self._suppressions)
        self._suppressions = [s for s in self._suppressions if s["type"] != alert_type]
        return len(self._suppressions) < before
    def get_active(self) -> list[dict[str, Any]]:
        now = time.time()
        return [s for s in self._suppressions if s["end_time"] > now]
    def cleanup(self) -> int:
        now = time.time()
        before = len(self._suppressions)
        self._suppressions = [s for s in self._suppressions if s["end_time"] > now]
        return before - len(self._suppressions)
