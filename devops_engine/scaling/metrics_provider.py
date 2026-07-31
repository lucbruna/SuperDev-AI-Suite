"""Metrics provider for autoscaling decisions (Volume 37, Fase 6)."""

from __future__ import annotations


class MetricsProvider:
    """Keeps recent utilization samples for scaling decisions."""

    def __init__(self) -> None:
        self._samples: dict[str, list[float]] = {}

    def record(self, metric: str, value: float) -> None:
        samples = self._samples.setdefault(metric, [])
        samples.append(float(value))
        if len(samples) > 100:
            del samples[:-100]

    def avg(self, metric: str, window: int | None = None) -> float:
        samples = self._samples.get(metric, [])
        if window is not None:
            samples = samples[-max(0, window):]
        return (sum(samples) / len(samples)) if samples else 0.0

    def last(self, metric: str) -> float:
        samples = self._samples.get(metric, [])
        return samples[-1] if samples else 0.0
