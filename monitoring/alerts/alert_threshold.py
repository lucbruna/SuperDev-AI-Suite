from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal


class ThresholdType:
    ABOVE = "above"
    BELOW = "below"
    BETWEEN = "between"
    OUTSIDE = "outside"
    CHANGE = "change"
    RATE = "rate"


@dataclass
class AlertThreshold:
    """Defines a threshold value and comparison type for alert rules."""

    metric: str = ""
    threshold_type: str = ThresholdType.ABOVE
    value: float = 0.0
    high_value: float = 0.0
    duration_seconds: float = 0.0
    description: str = ""

    def evaluate(self, current_value: float) -> bool:
        if self.threshold_type == ThresholdType.ABOVE:
            return current_value > self.value
        elif self.threshold_type == ThresholdType.BELOW:
            return current_value < self.value
        elif self.threshold_type == ThresholdType.BETWEEN:
            return self.value <= current_value <= self.high_value
        elif self.threshold_type == ThresholdType.OUTSIDE:
            return current_value < self.value or current_value > self.high_value
        return False

    def evaluate_series(self, values: list[float]) -> bool:
        if not values:
            return False

        if self.threshold_type == ThresholdType.CHANGE:
            baseline = values[0] if values else 0.0
            current = values[-1] if values else 0.0
            pct_change = (
                ((current - baseline) / abs(baseline or 1)) * 100
            )
            return abs(pct_change) > self.value

        if self.threshold_type == ThresholdType.RATE:
            if len(values) < 2:
                return False
            rate = (values[-1] - values[0]) / len(values)
            return abs(rate) > self.value

        if self.duration_seconds > 0 and len(values) > 0:
            firing = sum(1 for v in values if self.evaluate(v))
            return firing / len(values) > 0.5

        if not values:
            return False
        return self.evaluate(values[-1])
