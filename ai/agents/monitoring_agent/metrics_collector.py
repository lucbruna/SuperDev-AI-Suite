from __future__ import annotations

from typing import Any


class MetricsCollector:
    """Collects and summarizes metrics."""

    def __init__(self) -> None:
        self._metrics: dict[str, list[float]] = {}

    def collect(self, name: str, value: float) -> str:
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)
        return name

    def get_metric(self, name: str) -> list[float] | None:
        return self._metrics.get(name)

    def list_metrics(self) -> list[str]:
        return list(self._metrics.keys())

    @property
    def metric_count(self) -> int:
        return len(self._metrics)

    def summary(self, name: str) -> dict[str, float]:
        values = self._metrics.get(name, [])
        if not values:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "count": 0}
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": {k: v for k, v in self._metrics.items()},
            "metric_count": self.metric_count,
        }
