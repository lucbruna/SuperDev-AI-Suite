from __future__ import annotations

from typing import Any


class AnomalyDetector:
    """Detects anomalies in metric data using baseline statistics."""

    def __init__(self) -> None:
        self._baselines: dict[str, dict[str, float]] = {}

    def add_baseline(self, metric: str, mean: float, std: float) -> str:
        self._baselines[metric] = {"mean": mean, "std": std}
        return metric

    def get_baseline(self, metric: str) -> dict[str, float] | None:
        return self._baselines.get(metric)

    @property
    def baseline_count(self) -> int:
        return len(self._baselines)

    def detect(self, metric: str, value: float) -> dict[str, Any]:
        baseline = self._baselines.get(metric)
        if baseline is None:
            return {"metric": metric, "value": value, "anomaly": False, "reason": "no baseline"}
        lower = baseline["mean"] - 2 * baseline["std"]
        upper = baseline["mean"] + 2 * baseline["std"]
        is_anomaly = value < lower or value > upper
        return {
            "metric": metric,
            "value": value,
            "anomaly": is_anomaly,
            "lower_bound": lower,
            "upper_bound": upper,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "baselines": {k: v for k, v in self._baselines.items()},
            "baseline_count": self.baseline_count,
        }
