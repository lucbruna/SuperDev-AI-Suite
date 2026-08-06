"""Recommendation engine configuration."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.constants import (
    REC_ARCHITECTURE,
    REC_DEPENDENCY,
    REC_MODERNIZATION,
    REC_PERFORMANCE,
    REC_SECURITY,
)


@dataclass(slots=True)
class RecommendationConfig:
    """Deterministic recommendation scoring behaviour."""

    impact_weight: float = 0.5
    effort_weight: float = 0.2
    risk_weight: float = 0.3
    enabled_kinds: tuple[str, ...] = (
        REC_ARCHITECTURE,
        REC_DEPENDENCY,
        REC_PERFORMANCE,
        REC_SECURITY,
        REC_MODERNIZATION,
    )
