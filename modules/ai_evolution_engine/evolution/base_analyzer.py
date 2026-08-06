"""Base analyzer protocol for the AI Evolution Engine."""
from __future__ import annotations

from abc import ABC, abstractmethod

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_pipeline import AnalysisResult


class EvolutionAnalyzer(ABC):
    """Interface implemented by every deterministic analyzer."""

    dimension: str = "generic"

    @abstractmethod
    def analyze(self, ctx: EvolutionContext) -> AnalysisResult:
        raise NotImplementedError
