"""Architecture recommendations: coupling and modularity improvements."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    REC_ARCHITECTURE,
    SEVERITY_MAJOR,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


def generate(ctx: EvolutionContext) -> list[Recommendation]:
    coupling = float(ctx.get_artifact("coupling_ratio", 0.0) or 0.0)
    circular = int(ctx.get_artifact("circular_dependencies", 0) or 0)
    results: list[Recommendation] = []
    if coupling >= 0.5:
        results.append(
            Recommendation(
                kind=REC_ARCHITECTURE,
                title="Reduce module coupling",
                description=(
                    f"Coupling ratio {coupling:.2f} exceeds the healthy "
                    "threshold; review cross-module imports."
                ),
                target="platform",
                severity=SEVERITY_MAJOR,
                impact_score=min(coupling, 1.0),
                effort_score=0.6,
                risk_score=0.4,
                evidence=[f"coupling_ratio={coupling:.4f}"],
            )
        )
    if circular:
        results.append(
            Recommendation(
                kind=REC_ARCHITECTURE,
                title="Break circular dependency cycles",
                description=f"{circular} circular dependency detected.",
                target="platform",
                severity=SEVERITY_MAJOR,
                impact_score=min(0.4 + circular * 0.1, 1.0),
                effort_score=0.7,
                risk_score=0.5,
                evidence=[f"circular_dependencies={circular}"],
            )
        )
    return results
