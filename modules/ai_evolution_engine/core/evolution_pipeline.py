"""Pipeline orchestrating the full evolution cycle (deterministic)."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.constants import (
    ALL_PHASES,
    EVENT_ANALYSIS_COMPLETED,
    EVENT_RECOMMENDATION_CREATED,
    EVENT_ROADMAP_PLANNED,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class AnalysisResult:
    """Outcome of one analysis dimension (deterministic metrics)."""

    dimension: str
    score: float
    status: str
    metrics: dict[str, float] = field(default_factory=dict)
    findings: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "dimension": self.dimension,
            "score": self.score,
            "status": self.status,
            "metrics": self.metrics,
            "findings": self.findings,
        }


@dataclass(slots=True)
class EvolutionReport:
    """Aggregated analysis report for a full cycle."""

    status: str
    scores: dict[str, float] = field(default_factory=dict)
    results: list[AnalysisResult] = field(default_factory=list)
    phases_run: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "scores": self.scores,
            "results": [r.to_dict() for r in self.results],
            "phases_run": list(self.phases_run),
        }


class EvolutionPipeline:
    """Runs registered analyzers and aggregates their results.

    Deterministic: analyzer order is fixed by registration order and the
    aggregation is a pure reduction.
    """

    def __init__(self, analyzers: list | None = None) -> None:
        self._analyzers = list(analyzers or [])

    def register(self, analyzer) -> None:
        self._analyzers.append(analyzer)

    def analyzers(self) -> list:
        return list(self._analyzers)

    def run(self, ctx: EvolutionContext) -> EvolutionReport:
        ctx.state.increment_cycles(1)
        results: list[AnalysisResult] = []
        scores: dict[str, float] = {}
        phases: list[str] = [ALL_PHASES[0]]  # analyze
        for analyzer in self._analyzers:
            result = analyzer.analyze(ctx)
            if result is None:
                continue
            results.append(result)
            scores[result.dimension] = result.score
            ctx.set_artifact(f"analysis:{result.dimension}", result.to_dict())
        ctx.state.set_last_analysis_score(_overall(scores))
        ctx.publish(
            EVENT_ANALYSIS_COMPLETED,
            {"scores": scores, "dimensions": len(results)},
        )
        report = EvolutionReport(
            status="completed" if results else "empty",
            scores=scores,
            results=results,
            phases_run=phases,
        )
        ctx.set_artifact("report", report.to_dict())
        return report


def _overall(scores: dict[str, float]) -> float:
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)
