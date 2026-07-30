from __future__ import annotations

import math
from typing import Any


class CorrelationDetector:
    """Detects anomalies through cross-metric correlation analysis."""

    @staticmethod
    def pearson(values1: list[float], values2: list[float]) -> float:
        n = min(len(values1), len(values2))
        if n < 3:
            return 0.0
        v1 = values1[-n:]
        v2 = values2[-n:]
        mean1 = sum(v1) / n
        mean2 = sum(v2) / n
        num = sum((v1[i] - mean1) * (v2[i] - mean2) for i in range(n))
        den1 = math.sqrt(sum((v1[i] - mean1) ** 2 for i in range(n)))
        den2 = math.sqrt(sum((v2[i] - mean2) ** 2 for i in range(n)))
        if den1 == 0 or den2 == 0:
            return 0.0
        return num / (den1 * den2)

    @staticmethod
    def cross_correlation(values1: list[float], values2: list[float], lag: int = 1) -> float:
        n = min(len(values1), len(values2))
        if n < abs(lag) + 3:
            return 0.0
        if lag >= 0:
            v1 = values1[-(n - lag):]
            v2 = values2[-n:-lag]
        else:
            v1 = values1[-n:-abs(lag)]
            v2 = values2[-(n - abs(lag)):]
        return CorrelationDetector.pearson(v1, v2)

    @staticmethod
    def deviation_from_correlation(
        value1: float, value2: float,
        historical_correlation: float,
        threshold: float = 0.5,
    ) -> float:
        expected = historical_correlation
        actual = value1 * value2 if value1 and value2 else 0
        if abs(expected) < 0.01:
            return 0.0
        deviation = abs(actual - expected) / abs(expected)
        return deviation if deviation > threshold else 0.0
