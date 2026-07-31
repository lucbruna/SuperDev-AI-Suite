"""Metrics calculator."""

from __future__ import annotations


class MetricsCalculator:
    @staticmethod
    def rate(values: list[float], window: int = 10) -> float:
        if len(values) < 2 or window < 1:
            return 0.0
        recent = values[-window:]
        return (recent[-1] - recent[0]) / max(len(recent) - 1, 1)

    @staticmethod
    def moving_average(values: list[float], window: int = 5) -> float:
        if not values:
            return 0.0
        recent = values[-window:]
        return sum(recent) / len(recent)

    @staticmethod
    def standard_deviation(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance**0.5

    @staticmethod
    def z_score(value: float, values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        std = MetricsCalculator.standard_deviation(values)
        if std == 0:
            return 0.0
        return (value - mean) / std

    @staticmethod
    def trend(values: list[float]) -> str:
        if len(values) < 3:
            return "stable"
        first_half = sum(values[: len(values) // 2]) / max(len(values) // 2, 1)
        second_half = sum(values[len(values) // 2 :]) / max(len(values) // 2, 1)
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        return "stable"
