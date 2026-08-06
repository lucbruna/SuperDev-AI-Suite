"""Resource optimizer: usage and scaling suggestions."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.optimization.optimization_engine import (
    OptimizationSuggestion,
)


def suggest(ctx: EvolutionContext) -> list[OptimizationSuggestion]:
    usage = float(ctx.get_artifact("resource_usage_ratio", 0.0) or 0.0)
    if usage >= 0.85:
        return [
            OptimizationSuggestion(
                name="scale_resources",
                target="infrastructure",
                expected_impact=min((usage - 0.85) * 2.0, 1.0),
                effort=0.5,
            )
        ]
    return []
