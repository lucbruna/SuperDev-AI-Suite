"""Dependency optimizer: deduplication and pinning suggestions."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.optimization.optimization_engine import (
    OptimizationSuggestion,
)


def suggest(ctx: EvolutionContext) -> list[OptimizationSuggestion]:
    duplicates = int(ctx.get_artifact("duplicate_dependencies", 0) or 0)
    if duplicates < 3:
        return []
    return [
        OptimizationSuggestion(
            name="deduplicate_dependencies",
            target="dependencies",
            expected_impact=min(duplicates * 0.1, 1.0),
            effort=0.4,
        )
    ]
