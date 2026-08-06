"""Capacity forecast: headroom projection from usage ratio."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.forecasting.forecast_engine import (
    Forecast,
    linear_projection,
)


def forecast(ctx: EvolutionContext, horizon: int = 12) -> Forecast:
    usage = float(ctx.get_artifact("resource_usage_ratio", 0.0) or 0.0)
    growth = float(ctx.get_artifact("usage_growth_per_period", 0.02) or 0.02)
    return Forecast(
        name="capacity",
        values=[round(min(1.0, usage + growth * i), 4) for i in range(1, horizon + 1)],
        unit="ratio",
    )
