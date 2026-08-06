"""Shared test helpers for the AI Evolution Engine."""
from __future__ import annotations

from modules.ai_evolution_engine.config.evolution_config import EvolutionConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


def make_context(**artifacts: object) -> EvolutionContext:
    """Context with injected artifacts (deterministic fixtures)."""
    ctx = EvolutionContext(config=EvolutionConfig())
    for key, value in artifacts.items():
        ctx.set_artifact(key, value)
    return ctx


def make_recommendation(**overrides: object) -> Recommendation:
    fields: dict[str, object] = {
        "kind": "architecture",
        "title": "test recommendation",
        "impact_score": 0.8,
        "effort_score": 0.3,
        "risk_score": 0.2,
    }
    fields.update(overrides)
    return Recommendation(**fields)  # type: ignore[arg-type]
