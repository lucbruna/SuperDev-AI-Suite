"""Technical debt forecast: compounding interest projection."""
from __future__ import annotations

from modules.ai_evolution_engine.config.forecast_config import ForecastConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.forecasting.forecast_engine import (
    Forecast,
    compounding_projection,
)


def forecast(
    ctx: EvolutionContext,
    config: ForecastConfig | None = None,
    horizon: int = 12,
) -> Forecast:
    cfg = config or ForecastConfig()
    debt = float(ctx.get_artifact("debt_effort_points", 0.0) or 0.0)
    return Forecast(
        name="technical_debt",
        values=compounding_projection(debt, cfg.debt_interest_rate, horizon),
        unit="points",
    )
