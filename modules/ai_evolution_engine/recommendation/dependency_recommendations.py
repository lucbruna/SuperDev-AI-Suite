"""Dependency recommendations: upgrade and deduplication suggestions."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    REC_DEPENDENCY,
    SEVERITY_MINOR,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


def generate(ctx: EvolutionContext) -> list[Recommendation]:
    outdated = int(ctx.get_artifact("outdated_dependencies", 0) or 0)
    duplicates = int(ctx.get_artifact("duplicate_dependencies", 0) or 0)
    results: list[Recommendation] = []
    if outdated:
        results.append(
            Recommendation(
                kind=REC_DEPENDENCY,
                title="Upgrade outdated dependencies",
                description=f"{outdated} dependencies are outdated.",
                target="dependencies",
                severity=SEVERITY_MINOR,
                impact_score=min(outdated * 0.15, 1.0),
                effort_score=0.4,
                risk_score=0.3,
                evidence=[f"outdated_dependencies={outdated}"],
            )
        )
    if duplicates:
        results.append(
            Recommendation(
                kind=REC_DEPENDENCY,
                title="Deduplicate dependencies",
                description=f"{duplicates} duplicated dependencies detected.",
                target="dependencies",
                severity=SEVERITY_MINOR,
                impact_score=min(duplicates * 0.2, 1.0),
                effort_score=0.3,
                risk_score=0.2,
                evidence=[f"duplicate_dependencies={duplicates}"],
            )
        )
    return results
