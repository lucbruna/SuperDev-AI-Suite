from __future__ import annotations

from typing import Any


class SeasonalDetector:
    """Detects anomalies considering seasonal/periodic patterns."""

    @staticmethod
    def decomposition(values: list[float], period: int = 24) -> float:
        if len(values) < period * 2:
            return 0.0

        seasonal: list[float] = []
        for i in range(period):
            idxs = list(range(i, len(values) - 1, period))
            avg = sum(values[idx] for idx in idxs) / max(len(idxs), 1)
            seasonal.append(avg)

        seasonal_mean = sum(seasonal) / period
        seasonal_component = [s - seasonal_mean for s in seasonal]

        last_idx = (len(values) - 1) % period
        expected = seasonal_mean + seasonal_component[last_idx]
        actual = values[-1]

        residual = abs(actual - expected)
        residuals = [
            abs(values[i] - (seasonal_mean + seasonal_component[i % period]))
            for i in range(len(values) - 1)
        ]
        avg_residual = sum(residuals) / max(len(residuals), 1)

        if avg_residual == 0:
            return 0.0
        return residual / avg_residual

    @staticmethod
    def day_over_day(values: list[float], period: int = 24) -> float:
        if len(values) < period + 1:
            return 0.0
        expected = values[-period - 1] if len(values) > period else sum(values) / len(values)
        actual = values[-1]
        return abs(actual - expected) / (abs(expected) or 1)

    @staticmethod
    def week_over_week(values: list[float], daily_periods: int = 24) -> float:
        period = daily_periods * 7
        if len(values) < period + 1:
            return 0.0
        expected = values[-period - 1] if len(values) > period else sum(values) / len(values)
        actual = values[-1]
        return abs(actual - expected) / (abs(expected) or 1)
