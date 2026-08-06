"""Innovation engine: generates and ranks improvement ideas."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.innovation.opportunity_scorer import (
    Opportunity,
    OpportunityScorer,
)


class InnovationEngine:
    """Deterministic idea generation from context signals."""

    def __init__(self) -> None:
        self._scorer = OpportunityScorer()

    def generate(self, ctx: EvolutionContext) -> list[Opportunity]:
        candidates: list[Opportunity] = []
        duplication = int(ctx.get_artifact("duplicate_dependencies", 0) or 0)
        if duplication >= 3:
            candidates.append(
                Opportunity(
                    name="consolidate_dependencies",
                    value=0.7,
                    feasibility=0.8,
                    risk=0.2,
                )
            )
        cache_hit = float(ctx.get_artifact("cache_hit_ratio", 1.0) or 1.0)
        if cache_hit < 0.8:
            candidates.append(
                Opportunity(
                    name="introduce_caching",
                    value=0.8,
                    feasibility=0.7,
                    risk=0.3,
                )
            )
        test_pass = float(ctx.get_artifact("test_pass_rate", 1.0) or 1.0)
        if test_pass < 0.9:
            candidates.append(
                Opportunity(
                    name="harden_test_suite",
                    value=0.9,
                    feasibility=0.9,
                    risk=0.1,
                )
            )
        return self._scorer.rank(ctx, candidates)
