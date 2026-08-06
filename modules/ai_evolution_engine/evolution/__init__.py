"""Evolution analysis package."""
from __future__ import annotations

from modules.ai_evolution_engine.evolution.architecture_evolution import (
    ArchitectureEvolutionAnalyzer,
)
from modules.ai_evolution_engine.evolution.base_analyzer import EvolutionAnalyzer
from modules.ai_evolution_engine.evolution.codebase_evolution import (
    CodebaseEvolutionAnalyzer,
)
from modules.ai_evolution_engine.evolution.continuous_evolution import (
    ContinuousEvolutionAnalyzer,
)
from modules.ai_evolution_engine.evolution.dependency_evolution import (
    DependencyEvolutionAnalyzer,
)

__all__ = [
    "ArchitectureEvolutionAnalyzer",
    "CodebaseEvolutionAnalyzer",
    "ContinuousEvolutionAnalyzer",
    "DependencyEvolutionAnalyzer",
    "EvolutionAnalyzer",
]
