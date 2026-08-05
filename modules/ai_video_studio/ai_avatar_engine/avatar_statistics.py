"""Avatar statistics — track generation metrics and timings."""
from __future__ import annotations

import statistics
import time
from typing import Any


class AvatarStatistics:
    """Counts generations by profile/style and tracks durations."""

    def __init__(self) -> None:
        self._started = time.time()
        self._by_style: dict[str, int] = {}
        self._by_dimension: dict[str, int] = {}
        self._durations: list[float] = []

    def record(self, *, style: str, dimension: str, duration_ms: float) -> None:
        self._by_style[style] = self._by_style.get(style, 0) + 1
        self._by_dimension[dimension] = self._by_dimension.get(dimension, 0) + 1
        self._durations.append(duration_ms)

    def summary(self) -> dict[str, Any]:
        return {
            "uptime_seconds": round(time.time() - self._started, 2),
            "total": sum(self._by_style.values()),
            "by_style": dict(self._by_style),
            "by_dimension": dict(self._by_dimension),
            "avg_generation_ms": round(statistics.mean(self._durations), 2) if self._durations else 0.0,
        }

    def reset(self) -> None:
        self.__init__()


_avatar_statistics: AvatarStatistics | None = None


def get_avatar_statistics() -> AvatarStatistics:
    global _avatar_statistics
    if _avatar_statistics is None:
        _avatar_statistics = AvatarStatistics()
    return _avatar_statistics
