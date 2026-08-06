"""Performance optimizer: cache and latency suggestions."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.optimization.optimization_engine import (
    OptimizationSuggestion,
)


def suggest(ctx: EvolutionContext) -> list[OptimizationSuggestion]:
    suggestions: list[OptimizationSuggestion] = []
    cache_hit = float(ctx.get_artifact("cache_hit_ratio", 1.0) or 1.0)
    if cache_hit < 0.8:
        suggestions.append(
            OptimizationSuggestion(
                name="warm_cache",
                target="cache",
                expected_impact=round(0.8 - cache_hit, 4),
                effort=0.3,
            )
        )
    latency = float(ctx.get_artifact("p95_latency_ms", 0.0) or 0.0)
    if latency > 500:
        suggestions.append(
            OptimizationSuggestion(
                name="reduce_tail_latency",
                target="performance",
                expected_impact=min(latency / 2000.0, 1.0),
                effort=0.5,
            )
        )
    return suggestions
