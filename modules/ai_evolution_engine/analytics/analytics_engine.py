"""Analytics engine: aggregates platform metrics into structured analytics."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class Analytic:
    """One computed analytics slice."""

    name: str
    value: float
    unit: str = ""
    meta: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "meta": self.meta,
        }


class AnalyticsEngine:
    """Computes analytics slices from context artifacts and memory."""

    def __init__(self) -> None:
        self._slices: list[Analytic] = []

    def compute(self, ctx: EvolutionContext) -> list[Analytic]:
        """Deterministic aggregation of all known metrics."""
        slices: list[Analytic] = []
        slices.append(Analytic("platform_score", ctx.state.last_analysis_score))
        slices.append(
            Analytic(
                "open_recommendations",
                float(ctx.state.open_recommendations),
                unit="count",
            )
        )
        slices.append(
            Analytic("cycles", float(ctx.state.cycles), unit="count")
        )
        dependencies = ctx.get_artifact("dependency_count", 0) or 0
        slices.append(
            Analytic("dependency_count", float(dependencies), unit="count")
        )
        slices.append(
            Analytic(
                "duplicate_dependencies",
                float(ctx.get_artifact("duplicate_dependencies", 0) or 0),
                unit="count",
            )
        )
        self._slices = slices
        return list(self._slices)

    def slices(self) -> list[Analytic]:
        return list(self._slices)
