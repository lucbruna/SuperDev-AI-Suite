"""Runtime lifecycle state for the Security Engine (Volume 16)."""

from __future__ import annotations

import time
from typing import Any


class SecurityRuntime:
    """Tracks uptime and operation counters for the security engine."""

    def __init__(self) -> None:
        self._started_at: float | None = None
        self._operations: dict[str, int] = {}

    def start(self) -> None:
        if self._started_at is None:
            self._started_at = time.time()

    def stop(self) -> None:
        self._started_at = None

    def record(self, operation: str) -> None:
        self._operations[operation] = self._operations.get(operation, 0) + 1

    @property
    def is_running(self) -> bool:
        return self._started_at is not None

    @property
    def uptime(self) -> float:
        if self._started_at is None:
            return 0.0
        return round(time.time() - self._started_at, 2)

    def snapshot(self) -> dict[str, Any]:
        return {
            "running": self.is_running,
            "uptime": self.uptime,
            "operations": dict(self._operations),
        }
