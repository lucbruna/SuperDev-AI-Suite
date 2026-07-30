from __future__ import annotations

import math
from typing import Any


class MlDetector:
    """Lightweight ML-based anomaly detection using statistical models."""

    @staticmethod
    def moving_average(values: list[float], window: int = 10) -> float:
        if len(values) < 2:
            return 0.0
        recent = values[-window:] if len(values) >= window else values
        ma = sum(recent[:-1]) / max(len(recent) - 1, 1)
        return abs(values[-1] - ma) / (ma or 1)

    @staticmethod
    def exponential_smoothing(values: list[float], alpha: float = 0.3) -> float:
        if len(values) < 2:
            return 0.0
        smoothed = values[0]
        for v in values[:-1]:
            smoothed = alpha * v + (1 - alpha) * smoothed
        return abs(values[-1] - smoothed) / (smoothed or 1)

    @staticmethod
    def double_exponential_smoothing(values: list[float], alpha: float = 0.3, beta: float = 0.1) -> float:
        if len(values) < 3:
            return 0.0
        level = values[0]
        trend = values[1] - values[0]
        for v in values[:-1]:
            prev_level = level
            level = alpha * v + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend
        forecast = level + trend
        return abs(values[-1] - forecast) / (abs(forecast) or 1)

    @staticmethod
    def grubbs_test(values: list[float], alpha: float = 0.05) -> float:
        import statistics
        n = len(values)
        if n < 3:
            return 0.0
        mean = statistics.mean(values)
        std = statistics.stdev(values) if statistics.stdev(values) > 0 else 1.0
        g = max(abs(v - mean) / std for v in values)

        import math
        t_crit = 2.0
        if n > 3:
            from scipy import stats  # type: ignore[import-untyped]
            try:
                t_crit = stats.t.ppf(1 - alpha / (2 * n), n - 2)
            except Exception:
                t_crit = 2.0

        g_crit = ((n - 1) / math.sqrt(n)) * math.sqrt(
            t_crit ** 2 / (n - 2 + t_crit ** 2)
        )
        if g > g_crit:
            return (g - g_crit) / g_crit * 10
        return 0.0
