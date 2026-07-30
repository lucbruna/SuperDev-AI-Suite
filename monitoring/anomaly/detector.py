from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import AnomalyScore


@dataclass
class DetectorConfig:
    window_size: int = 100
    sensitivity: float = 2.0
    min_samples: int = 10
    enabled: bool = True


class AnomalyDetector:
    """Base anomaly detector that applies detection methods to metric data."""

    def __init__(self, config: DetectorConfig | None = None) -> None:
        self._config = config or DetectorConfig()
        self._methods: list[Callable[[list[float]], float]] = []
        self._results: list[AnomalyScore] = []
        self._callbacks: list[Callable[[AnomalyScore], None]] = []

    def add_method(self, method: Callable[[list[float]], float]) -> None:
        self._methods.append(method)

    def analyze(self, metric_name: str, values: list[float]) -> list[AnomalyScore]:
        scores: list[AnomalyScore] = []
        if len(values) < self._config.min_samples:
            return scores

        for method in self._methods:
            try:
                deviation = method(values)
                current = values[-1] if values else 0.0
                baseline = sum(values[:-1]) / max(len(values) - 1, 1) if len(values) > 1 else current

                score = AnomalyScore(
                    metric=metric_name,
                    score=min(abs(deviation), 100.0),
                    baseline=baseline,
                    current=current,
                    deviation=deviation,
                    is_anomaly=abs(deviation) > self._config.sensitivity,
                )
                scores.append(score)
                self._results.append(score)
                self._notify(score)
            except Exception:
                pass

        return scores

    def on_anomaly(self, callback: Callable[[AnomalyScore], None]) -> None:
        self._callbacks.append(callback)

    def _notify(self, score: AnomalyScore) -> None:
        if not score.is_anomaly:
            return
        for cb in self._callbacks:
            try:
                cb(score)
            except Exception:
                pass

    def get_results(self, limit: int = 100) -> list[AnomalyScore]:
        return list(self._results[-limit:])

    def clear(self) -> None:
        self._results.clear()
