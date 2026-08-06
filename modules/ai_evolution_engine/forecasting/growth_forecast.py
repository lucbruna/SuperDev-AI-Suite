"""Growth forecast: linear projection of platform size."""
from __future__ import annotations

from modules.ai_evolution_engine.config.forecast_config import ForecastConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.forecasting.forecast_engine import (
    Forecast,
    linear_projection,
)


def forecast(
    ctx: EvolutionContext,
    config: ForecastConfig | None = None,
    horizon: int = 12,
) -> Forecast:
    cfg = config or ForecastConfig()
    modules = float(ctx.get_artifact("module_count", 1.0) or 1.0)
    delta = modules * cfg.capacity_growth_rate
    return Forecast(
        name="growth",
        values=linear_projection(modules, delta, horizon),
        unit="modules",
    )
