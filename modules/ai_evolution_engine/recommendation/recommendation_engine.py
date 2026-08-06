"""Recommendation engine: produces and scores recommendations."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import SEVERITY_INFO
from modules.ai_evolution_engine.config.recommendation_config import (
    RecommendationConfig,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


class RecommendationEngine:
    """Runs registered generators and scores their output."""

    def __init__(
        self,
        config: RecommendationConfig | None = None,
        generators: list | None = None,
    ) -> None:
        self._config = config or RecommendationConfig()
        self._generators = list(generators or [])

    def register(self, generator) -> None:
        self._generators.append(generator)

    def generate(self, ctx: EvolutionContext) -> list[Recommendation]:
        collected: list[Recommendation] = []
        for generator in self._generators:
            for item in generator(ctx):
                if not isinstance(item, Recommendation):
                    continue
                if item.kind not in self._config.enabled_kinds:
                    continue
                collected.append(item)
        collected.sort(key=lambda r: r.priority(
            self._config.impact_weight,
            self._config.effort_weight,
            self._config.risk_weight,
        ), reverse=True)
        return collected
