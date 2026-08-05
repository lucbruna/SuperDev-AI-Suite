"""Animation statistics — track animation render metrics."""
from __future__ import annotations

import statistics
import time
from typing import Any


class AnimationStatistics:
    """Counts animations by action and tracks render times."""

    def __init__(self) -> None:
        self._started = time.time()
        self._counts: dict[str, int] = {}
        self._durations: list[float] = []

    def record(self, *, action: str, duration_ms: float) -> None:
        self._counts[action] = self._counts.get(action, 0) + 1
        self._durations.append(duration_ms)

    def summary(self) -> dict[str, Any]:
        return {
            "uptime_seconds": round(time.time() - self._started, 2),
            "total": sum(self._counts.values()),
            "per_action": dict(self._counts),
            "avg_render_ms": round(statistics.mean(self._durations), 2) if self._durations else 0.0,
        }

    def reset(self) -> None:
        self.__init__()


_animation_statistics: AnimationStatistics | None = None


def get_animation_statistics() -> AnimationStatistics:
    global _animation_statistics
    if _animation_statistics is None:
        _animation_statistics = AnimationStatistics()
    return _animation_statistics
