"""Manual tick-based scheduler for index refreshes."""

from __future__ import annotations

import time
from typing import Any, Callable


class IndexScheduler:
    """Runs a refresh callback; supports frequency and manual triggers."""

    def __init__(self, frequency_seconds: float = 300.0) -> None:
        self.frequency_seconds = max(1.0, frequency_seconds)
        self._last_run = 0.0
        self._runs = 0

    def due(self, now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        return (now - self._last_run) >= self.frequency_seconds

    def run_if_due(self, callback: Callable[[], Any],
                   now: float | None = None) -> bool:
        if not self.due(now):
            return False
        self._last_run = time.time()
        self._runs += 1
        callback()
        return True

    def trigger(self, callback: Callable[[], Any]) -> None:
        self._last_run = time.time()
        self._runs += 1
        callback()

    @property
    def runs(self) -> int:
        return self._runs
