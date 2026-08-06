"""Forecasting package for the AI Evolution Engine."""
from __future__ import annotations

from modules.ai_evolution_engine.forecasting.forecast_engine import (
    Forecast,
    ForecastEngine,
    compounding_projection,
    linear_projection,
)

__all__ = [
    "Forecast",
    "ForecastEngine",
    "compounding_projection",
    "linear_projection",
]
