from __future__ import annotations

import time
from typing import Any


class WorkerMetrics:
    """Tracks worker performance metrics."""

    def __init__(self) -> None:
        self._submissions = 0
        self._completions = 0
        self._failures = 0
        self._start_time = time.time()

    def record_submission(self) -> None:
        self._submissions += 1

    def record_completion(self) -> None:
        self._completions += 1

    def record_failure(self) -> None:
        self._failures += 1

    def snapshot(self) -> dict[str, Any]:
        uptime = time.time() - self._start_time
        return {
            "submissions": self._submissions,
            "completions": self._completions,
            "failures": self._failures,
            "uptime_seconds": uptime,
        }
