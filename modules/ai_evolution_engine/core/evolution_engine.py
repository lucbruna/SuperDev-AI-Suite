"""Evolution engine: single-cycle entry point (deterministic)."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_pipeline import (
    EvolutionPipeline,
    EvolutionReport,
)


@dataclass(slots=True)
class EngineResult:
    """Result of one engine cycle."""

    report: EvolutionReport
    recommendations: list[object] = field(default_factory=list)
    decisions: list[object] = field(default_factory=list)
    status: str = "ok"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "report": self.report.to_dict(),
            "recommendations": [r.to_dict() for r in self.recommendations],
            "decisions": [d.to_dict() for d in self.decisions],
        }


class EvolutionEngine:
    """Runs the analysis pipeline inside a context."""

    def __init__(self, pipeline: EvolutionPipeline | None = None) -> None:
        self._pipeline = pipeline or EvolutionPipeline()

    @property
    def pipeline(self) -> EvolutionPipeline:
        return self._pipeline

    def run(
        self,
        ctx: EvolutionContext,
        recommendations: list | None = None,
        decisions: list | None = None,
    ) -> EngineResult:
        report = self._pipeline.run(ctx)
        return EngineResult(
            report=report,
            recommendations=list(recommendations or []),
            decisions=list(decisions or []),
        )
