"""Seasonal forecasting with period factors (carnival boost example)."""

from __future__ import annotations

from typing import Any

from data_intelligence.forecasting.base import (ForecastError, Forecaster)


class SeasonalForecaster(Forecaster):
    """Learns per-season multipliers and forecasts future seasons.

    ``fit`` receives labelled points as ``(period_key, value)`` pairs or a
    ``{period_key: value}`` mapping.  The season component is the last
    ``-``-separated segment of the key (e.g. ``2025-02`` -> ``02``), so the
    factor for ``02`` captures events like the carnival boost on drinks.
    ``forecast(period_key)`` returns the overall mean times that season's
    factor.
    """

    def __init__(self) -> None:
        self.factors: dict[str, float] = {}
        self.baseline: float = 0.0

    def fit(self, values: Any) -> "SeasonalForecaster":
        if isinstance(values, dict):
            pairs = [(str(key), float(value))
                     for key, value in values.items()]
        else:
            pairs = [(str(key), float(value)) for key, value in values]
        if not pairs:
            raise ForecastError("cannot fit an empty series")
        self.pairs = pairs
        overall = [value for _, value in pairs]
        self.baseline = sum(overall) / len(overall)
        by_season: dict[str, list[float]] = {}
        for key, value in pairs:
            by_season.setdefault(self._season(key), []).append(value)
        self.factors = {
            season: sum(vals) / len(vals) / self.baseline
            for season, vals in by_season.items()}
        return self

    def forecast(self, steps: int, period_key: str | None = None) -> list[float]:
        if not hasattr(self, "pairs"):
            raise ForecastError("forecaster not fitted")
        key = period_key or self.pairs[-1][0]
        season = self._season(key)
        factor = self.factors.get(season, 1.0)
        return [self.baseline * factor] * steps

    @staticmethod
    def _season(key: str) -> str:
        return key.split("-")[-1]
