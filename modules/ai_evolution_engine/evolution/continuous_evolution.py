"""Continuous evolution analysis: aggregates platform health signals."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import SEVERITY_INFO
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_pipeline import AnalysisResult
from modules.ai_evolution_engine.evolution.base_analyzer import EvolutionAnalyzer


class ContinuousEvolutionAnalyzer(EvolutionAnalyzer):
    """Runs every cycle; reports an overall platform evolution score.

    Deterministic: the score is derived from persisted analysis artifacts and
    learning statistics stored in the context memory.
    """

    dimension = "continuous"

    def analyze(self, ctx: EvolutionContext) -> AnalysisResult:
        artifact_score = float(ctx.get_artifact("platform_score", 0.0) or 0.0)
        patterns = len(ctx.memory.recall("learned_patterns", []) or [])
        incidents = len(ctx.memory.recall("learned_incidents", []) or [])
        improvements = int(ctx.memory.recall("improvements_applied", 0) or 0)

        score = round(0.6 * artifact_score + 0.2 * min(patterns, 50) / 50 * 100 + 0.2 * min(improvements, 10) / 10 * 100, 2)
        return AnalysisResult(
            dimension=self.dimension,
            score=score,
            status="healthy" if score >= 70 else ("degraded" if score >= 40 else "critical"),
            metrics={
                "platform_score": artifact_score,
                "learned_patterns": patterns,
                "learned_incidents": incidents,
                "improvements_applied": improvements,
            },
            findings=[],
        )
