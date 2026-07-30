from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ReasoningMetrics:
    """Collects and reports reasoning performance metrics."""

    def __init__(self):
        self._total_reasoning_calls = 0
        self._total_reasoning_time = 0.0
        self._total_hypotheses = 0
        self._confidence_sum = 0.0
        self._start_time = datetime.now(timezone.utc)

    def record_reasoning(self, duration_ms: float, confidence: float) -> None:
        self._total_reasoning_calls += 1
        self._total_reasoning_time += duration_ms
        self._confidence_sum += confidence

    def record_hypothesis(self) -> None:
        self._total_hypotheses += 1

    def snapshot(self) -> dict[str, Any]:
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
        return {
            "total_reasoning_calls": self._total_reasoning_calls,
            "avg_duration_ms": self._total_reasoning_time / max(self._total_reasoning_calls, 1),
            "total_hypotheses": self._total_hypotheses,
            "avg_confidence": self._confidence_sum / max(self._total_reasoning_calls, 1),
            "uptime_seconds": uptime,
        }

    def reset(self) -> None:
        self.__init__()
