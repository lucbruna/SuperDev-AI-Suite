"""Modernization recommendations: legacy signals and upgrades."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    REC_MODERNIZATION,
    SEVERITY_INFO,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


def generate(ctx: EvolutionContext) -> list[Recommendation]:
    legacy = int(ctx.get_artifact("legacy_components", 0) or 0)
    results: list[Recommendation] = []
    if legacy:
        results.append(
            Recommendation(
                kind=REC_MODERNIZATION,
                title="Plan modernization of legacy components",
                description=f"{legacy} components flagged as legacy.",
                target="legacy",
                severity=SEVERITY_INFO,
                impact_score=min(legacy * 0.25, 1.0),
                effort_score=0.8,
                risk_score=0.6,
                evidence=[f"legacy_components={legacy}"],
            )
        )
    return results
