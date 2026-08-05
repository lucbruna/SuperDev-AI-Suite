"""Generation statistics — collect and report generation metrics."""
from __future__ import annotations

import statistics
import time
from typing import Any


class GenerationStatistics:
    """Tracks per-mode generation counts, durations and quality scores."""

    def __init__(self) -> None:
        self._started = time.time()
        self._counts: dict[str, int] = {}
        self._durations: dict[str, list[float]] = {}
        self._quality: dict[str, list[float]] = {}
        self._failures = 0

    def record(
        self,
        *,
        mode: str,
        duration_ms: float,
        quality_score: float | None = None,
        success: bool = True,
    ) -> None:
        if not success:
            self._failures += 1
        self._counts[mode] = self._counts.get(mode, 0) + 1
        self._durations.setdefault(mode, []).append(duration_ms)
        if quality_score is not None:
            self._quality.setdefault(mode, []).append(quality_score)

    def summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "uptime_seconds": round(time.time() - self._started, 2),
            "failures": self._failures,
            "total": sum(self._counts.values()),
            "per_mode": {},
        }
        for mode in self._counts:
            durations = self._durations.get(mode, [])
            qualities = self._quality.get(mode, [])
            result["per_mode"][mode] = {
                "count": self._counts[mode],
                "avg_duration_ms": round(statistics.mean(durations), 2) if durations else 0.0,
                "avg_quality": round(statistics.mean(qualities), 3) if qualities else None,
            }
        return result

    def reset(self) -> None:
        self.__init__()


_generation_statistics: GenerationStatistics | None = None


def get_generation_statistics() -> GenerationStatistics:
    global _generation_statistics
    if _generation_statistics is None:
        _generation_statistics = GenerationStatistics()
    return _generation_statistics
