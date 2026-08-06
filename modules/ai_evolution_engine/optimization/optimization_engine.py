"""Optimization engine: deterministic improvement suggestions."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.optimization_config import (
    OptimizationConfig,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class OptimizationSuggestion:
    """One proposed optimization (never applied automatically)."""

    name: str
    target: str
    expected_impact: float
    effort: float

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "target": self.target,
            "expected_impact": self.expected_impact,
            "effort": self.effort,
        }


class OptimizationEngine:
    """Derives suggestions from context artifacts."""

    def __init__(self, config: OptimizationConfig | None = None) -> None:
        self._config = config or OptimizationConfig()

    def suggest(self, ctx: EvolutionContext) -> list[OptimizationSuggestion]:
        suggestions: list[OptimizationSuggestion] = []
        cache_hit = float(ctx.get_artifact("cache_hit_ratio", 1.0) or 1.0)
        if cache_hit < self._config.cache_hit_target:
            suggestions.append(
                OptimizationSuggestion(
                    name="warm_cache",
                    target="cache",
                    expected_impact=self._config.cache_hit_target - cache_hit,
                    effort=0.3,
                )
            )
        duplicates = int(ctx.get_artifact("duplicate_dependencies", 0) or 0)
        if duplicates >= self._config.dependency_duplication_threshold:
            suggestions.append(
                OptimizationSuggestion(
                    name="deduplicate_dependencies",
                    target="dependencies",
                    expected_impact=min(duplicates * 0.1, 1.0),
                    effort=0.4,
                )
            )
        large = int(ctx.get_artifact("large_files", 0) or 0)
        if large:
            suggestions.append(
                OptimizationSuggestion(
                    name="split_large_files",
                    target="codebase",
                    expected_impact=min(large * 0.15, 1.0),
                    effort=0.6,
                )
            )
        return suggestions[: self._config.max_suggestions_per_cycle]
