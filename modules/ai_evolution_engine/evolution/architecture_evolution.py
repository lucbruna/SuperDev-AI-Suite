"""Architecture evolution analysis: coupling and cohesion signals."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import SEVERITY_MAJOR
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_pipeline import AnalysisResult
from modules.ai_evolution_engine.evolution.base_analyzer import EvolutionAnalyzer


class ArchitectureEvolutionAnalyzer(EvolutionAnalyzer):
    """Scores architecture health from coupling metrics.

    Inputs (via artifacts or memory, optional): ``coupling_ratio`` (0..1),
    ``circular_dependencies`` (count), ``module_count``. Higher coupling and
    more circular dependencies lower the score.
    """

    dimension = "architecture"

    def analyze(self, ctx: EvolutionContext) -> AnalysisResult:
        coupling = float(ctx.get_artifact("coupling_ratio", 0.0) or 0.0)
        circular = int(ctx.get_artifact("circular_dependencies", 0) or 0)
        module_count = int(ctx.get_artifact("module_count", 1) or 1)

        coupling_penalty = coupling * 50
        circular_penalty = min(circular, 10) * 4
        score = round(max(0.0, 100.0 - coupling_penalty - circular_penalty), 2)

        findings = []
        if circular:
            findings.append(
                {
                    "severity": SEVERITY_MAJOR,
                    "message": f"{circular} circular dependencies detected",
                    "module_count": module_count,
                }
            )
        return AnalysisResult(
            dimension=self.dimension,
            score=score,
            status="healthy" if score >= 70 else ("degraded" if score >= 40 else "critical"),
            metrics={
                "coupling_ratio": coupling,
                "circular_dependencies": circular,
                "module_count": module_count,
            },
            findings=findings,
        )
