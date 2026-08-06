"""Performance recommendations: response and resource signals."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    REC_PERFORMANCE,
    SEVERITY_MAJOR,
    SEVERITY_MINOR,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


def generate(ctx: EvolutionContext) -> list[Recommendation]:
    latency = float(ctx.get_artifact("p95_latency_ms", 0.0) or 0.0)
    cache_hit = float(ctx.get_artifact("cache_hit_ratio", 1.0) or 1.0)
    results: list[Recommendation] = []
    if latency > 500:
        results.append(
            Recommendation(
                kind=REC_PERFORMANCE,
                title="Investigate high tail latency",
                description=f"p95 latency {latency:.0f}ms exceeds budget.",
                target="performance",
                severity=SEVERITY_MAJOR,
                impact_score=min(latency / 2000.0, 1.0),
                effort_score=0.5,
                risk_score=0.3,
                evidence=[f"p95_latency_ms={latency}"],
            )
        )
    if cache_hit < 0.8:
        results.append(
            Recommendation(
                kind=REC_PERFORMANCE,
                title="Improve cache hit ratio",
                description=f"Cache hit ratio {cache_hit:.2f} is below target.",
                target="performance",
                severity=SEVERITY_MINOR,
                impact_score=(0.8 - cache_hit) / 0.8,
                effort_score=0.4,
                risk_score=0.2,
                evidence=[f"cache_hit_ratio={cache_hit}"],
            )
        )
    return results
