from __future__ import annotations

import time
from typing import Any


class ProjectMetrics:
    """Tracks project-level metrics."""

    def __init__(self) -> None:
        self._creations = 0
        self._completions = 0
        self._start_time = time.time()

    def record_creation(self) -> None:
        self._creations += 1

    def record_completion(self) -> None:
        self._completions += 1

    def snapshot(self) -> dict[str, Any]:
        return {
            "creations": self._creations,
            "completions": self._completions,
            "uptime_seconds": time.time() - self._start_time,
        }
