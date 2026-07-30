from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class ReasoningMetrics:
    """Metrics for reasoning engine performance."""

    def __init__(self) -> None:
        self._reasoning_steps: int = 0
        self._depth: int = 0

    def record_step(self, depth: int = 0) -> list[MetricSample]:
        self._reasoning_steps += 1
        self._depth = max(self._depth, depth)
        return [
            MetricSample("reasoning_steps_total", 1.0, metric_type=MetricType.COUNTER),
            MetricSample("reasoning_max_depth", float(self._depth), metric_type=MetricType.GAUGE),
        ]

    def snapshot(self) -> dict[str, Any]:
        return {"steps": self._reasoning_steps, "max_depth": self._depth}


__all__ = ["ReasoningMetrics"]
