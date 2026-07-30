from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class Counter:
    """Monotonically increasing counter metric."""

    def __init__(self, name: str, labels: dict[str, str] | None = None) -> None:
        self._name = name
        self._labels = labels or {}
        self._value: float = 0.0

    def inc(self, value: float = 1.0) -> MetricSample:
        self._value += value
        return MetricSample(
            name=self._name, value=self._value,
            labels=self._labels, metric_type=MetricType.COUNTER,
        )

    @property
    def value(self) -> float:
        return self._value

    def reset(self) -> None:
        self._value = 0.0


__all__ = ["Counter"]
