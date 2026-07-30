from __future__ import annotations

from typing import Any


class ThresholdDetector:
    """Detects anomalies based on fixed or dynamic thresholds."""

    @staticmethod
    def fixed(values: list[float], min_val: float = -float("inf"), max_val: float = float("inf")) -> float:
        if not values:
            return 0.0
        last = values[-1]
        if last > max_val:
            return (last - max_val) / (max_val or 1) * 10
        if last < min_val:
            return (min_val - last) / (min_val or 1) * 10
        return 0.0

    @staticmethod
    def rate_of_change(values: list[float], max_rate: float = 1.0) -> float:
        if len(values) < 2:
            return 0.0
        changes = [abs(values[i] - values[i - 1]) / max(abs(values[i - 1]), 0.001) for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)
        last_change = changes[-1]
        if last_change > avg_change * max_rate:
            return (last_change - avg_change * max_rate) / (avg_change * max_rate or 1) * 10
        return 0.0

    @staticmethod
    def cumulative(values: list[float], baseline: float | None = None) -> float:
        if not values:
            return 0.0
        avg = baseline or (sum(values) / len(values))
        cum_sum = sum(v - avg for v in values)
        return abs(cum_sum) / (abs(avg) or 1)
