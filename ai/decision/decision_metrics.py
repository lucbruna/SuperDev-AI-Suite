from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class DecisionMetrics:
    """Metrics collection for decision performance."""

    def __init__(self):
        self._total_decisions = 0
        self._total_evaluation_time = 0.0
        self._confidence_sum = 0.0
        self._start_time = datetime.now(UTC)

    def record_decision(self, duration_ms: float, confidence: float) -> None:
        self._total_decisions += 1
        self._total_evaluation_time += duration_ms
        self._confidence_sum += confidence

    def snapshot(self) -> dict[str, Any]:
        uptime = (datetime.now(UTC) - self._start_time).total_seconds()
        return {
            "total_decisions": self._total_decisions,
            "avg_duration_ms": self._total_evaluation_time / max(self._total_decisions, 1),
            "avg_confidence": self._confidence_sum / max(self._total_decisions, 1),
            "uptime_seconds": uptime,
        }
