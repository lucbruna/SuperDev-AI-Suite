"""Opportunity scorer: ranks innovation candidates deterministically."""
from __future__ import annotations

from dataclasses import dataclass

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class Opportunity:
    """A ranked innovation candidate."""

    name: str
    value: float
    feasibility: float
    risk: float

    @property
    def score(self) -> float:
        return round(self.value * 0.5 + self.feasibility * 0.3 - self.risk * 0.2, 4)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "feasibility": self.feasibility,
            "risk": self.risk,
            "score": self.score,
        }


class OpportunityScorer:
    """Ranks opportunities by a fixed weighted formula."""

    def rank(
        self, ctx: EvolutionContext, candidates: list[Opportunity]
    ) -> list[Opportunity]:
        return sorted(candidates, key=lambda o: o.score, reverse=True)
