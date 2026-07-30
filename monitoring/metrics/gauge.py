from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class Gauge:
    """Point-in-time metric that can go up or down."""

    def __init__(self, name: str, labels: dict[str, str] | None = None) -> None:
        self._name = name
        self._labels = labels or {}
        self._value: float = 0.0

    def set(self, value: float) -> MetricSample:
        self._value = value
        return MetricSample(
            name=self._name, value=self._value,
            labels=self._labels, metric_type=MetricType.GAUGE,
        )

    def inc(self, delta: float = 1.0) -> MetricSample:
        self._value += delta
        return self.set(self._value)

    def dec(self, delta: float = 1.0) -> MetricSample:
        self._value -= delta
        return self.set(self._value)

    @property
    def value(self) -> float:
        return self._value


__all__ = ["Gauge"]
