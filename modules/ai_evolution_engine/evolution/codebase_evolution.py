"""Codebase evolution analysis: size and complexity signals."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import SEVERITY_MAJOR
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_pipeline import AnalysisResult
from modules.ai_evolution_engine.evolution.base_analyzer import EvolutionAnalyzer


class CodebaseEvolutionAnalyzer(EvolutionAnalyzer):
    """Scores codebase maintainability from size/complexity signals.

    Inputs: ``large_files`` (count), ``high_complexity`` (count),
    ``total_files``. Large or complex files penalise the score.
    """

    dimension = "codebase"

    def analyze(self, ctx: EvolutionContext) -> AnalysisResult:
        large = int(ctx.get_artifact("large_files", 0) or 0)
        complex_units = int(ctx.get_artifact("high_complexity", 0) or 0)
        total = int(ctx.get_artifact("total_files", 0) or 0)

        large_penalty = min(large, 10) * 4
        complexity_penalty = min(complex_units, 10) * 3
        score = round(max(0.0, 100.0 - large_penalty - complexity_penalty), 2)

        findings = []
        if large:
            findings.append(
                {
                    "severity": SEVERITY_MAJOR,
                    "message": f"{large} files exceed size threshold; consider splitting",
                    "total_files": total,
                }
            )
        return AnalysisResult(
            dimension=self.dimension,
            score=score,
            status="healthy" if score >= 70 else ("degraded" if score >= 40 else "critical"),
            metrics={
                "large_files": large,
                "high_complexity": complex_units,
                "total_files": total,
            },
            findings=findings,
        )
