"""Metric store for monitoring (Volume 37, Fase 4)."""

from __future__ import annotations

from devops_engine.devops_models import MetricSample
from devops_engine.devops_protocols import new_id, now


class MetricStore:
    """Records and aggregates metric samples by name."""

    def __init__(self) -> None:
        self._samples: dict[str, list[MetricSample]] = {}

    def record(self, name: str, value: float, unit: str = "",
               source: str = "") -> MetricSample:
        sample = MetricSample(
            metric_id=new_id("metric"),
            name=name,
            value=float(value),
            unit=unit,
            source=source,
            sampled_at=now(),
        )
        self._samples.setdefault(name, []).append(sample)
        return sample

    def get(self, name: str) -> list[MetricSample]:
        return list(self._samples.get(name, []))

    def last(self, name: str) -> MetricSample | None:
        samples = self._samples.get(name, [])
        return samples[-1] if samples else None

    def avg(self, name: str) -> float:
        samples = self._samples.get(name, [])
        return (sum(s.value for s in samples) / len(samples)
                if samples else 0.0)

    def max(self, name: str) -> float:
        samples = self._samples.get(name, [])
        return max((s.value for s in samples), default=0.0)

    def count(self) -> int:
        return sum(len(samples) for samples in self._samples.values())
