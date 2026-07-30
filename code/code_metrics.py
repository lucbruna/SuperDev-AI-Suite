from __future__ import annotations

import time
from typing import Any


class CodeMetrics:
    """Tracks code analysis and generation metrics."""

    def __init__(self) -> None:
        self._files_scanned = 0
        self._files_generated = 0
        self._start_time = time.time()

    def record_scan(self, count: int = 1) -> None:
        self._files_scanned += count

    def record_generation(self, count: int = 1) -> None:
        self._files_generated += count

    def snapshot(self) -> dict[str, Any]:
        return {
            "files_scanned": self._files_scanned,
            "files_generated": self._files_generated,
            "uptime_seconds": time.time() - self._start_time,
        }
