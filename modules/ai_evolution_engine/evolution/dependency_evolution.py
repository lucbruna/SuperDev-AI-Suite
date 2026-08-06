"""Dependency evolution analysis: dependency health signals."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import SEVERITY_MINOR
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_pipeline import AnalysisResult
from modules.ai_evolution_engine.evolution.base_analyzer import EvolutionAnalyzer


class DependencyEvolutionAnalyzer(EvolutionAnalyzer):
    """Scores dependency hygiene.

    Inputs: ``outdated_dependencies`` (count), ``dependency_count``,
    ``duplicate_dependencies`` (count).
    """

    dimension = "dependency"

    def analyze(self, ctx: EvolutionContext) -> AnalysisResult:
        outdated = int(ctx.get_artifact("outdated_dependencies", 0) or 0)
        total = int(ctx.get_artifact("dependency_count", 0) or 0)
        duplicates = int(ctx.get_artifact("duplicate_dependencies", 0) or 0)

        outdated_penalty = min(outdated, 10) * 5
        duplicate_penalty = min(duplicates, 10) * 3
        score = round(max(0.0, 100.0 - outdated_penalty - duplicate_penalty), 2)

        findings = []
        if outdated:
            findings.append(
                {
                    "severity": SEVERITY_MINOR,
                    "message": f"{outdated} outdated dependencies",
                    "total": total,
                }
            )
        return AnalysisResult(
            dimension=self.dimension,
            score=score,
            status="healthy" if score >= 70 else ("degraded" if score >= 40 else "critical"),
            metrics={
                "outdated_dependencies": outdated,
                "dependency_count": total,
                "duplicate_dependencies": duplicates,
            },
            findings=findings,
        )
