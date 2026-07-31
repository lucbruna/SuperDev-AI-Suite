from __future__ import annotations

import time
from typing import Any


class DataRuntime:
    """Runtime state context for the Data & Analytics Engine."""

    def __init__(self) -> None:
        self._started_at: float | None = None
        self._metadata: dict[str, Any] = {}
        self._counters: dict[str, int] = {}
        self._active_batches: int = 0
        self._active_pipelines: int = 0

    def start(self) -> None:
        self._started_at = time.time()

    @property
    def uptime(self) -> float:
        if self._started_at is None:
            return 0.0
        return time.time() - self._started_at

    @property
    def started_at(self) -> float | None:
        return self._started_at

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def get_metadata(self, key: str) -> Any:
        return self._metadata.get(key)

    def increment(self, counter: str, delta: int = 1) -> int:
        self._counters[counter] = self._counters.get(counter, 0) + delta
        return self._counters[counter]

    def get_counter(self, counter: str) -> int:
        return self._counters.get(counter, 0)

    def begin_batch(self) -> None:
        self._active_batches += 1

    def end_batch(self) -> None:
        self._active_batches = max(0, self._active_batches - 1)

    def begin_pipeline(self) -> None:
        self._active_pipelines += 1

    def end_pipeline(self) -> None:
        self._active_pipelines = max(0, self._active_pipelines - 1)

    def snapshot(self) -> dict[str, Any]:
        return {
            "uptime": self.uptime,
            "started_at": self.started_at,
            "active_batches": self._active_batches,
            "active_pipelines": self._active_pipelines,
            "counters": dict(self._counters),
            "metadata": dict(self._metadata),
        }


__all__ = ["DataRuntime"]
