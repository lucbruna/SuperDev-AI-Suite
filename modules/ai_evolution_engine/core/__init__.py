"""Core package for the AI Evolution Engine."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_engine import (
    EngineResult,
    EvolutionEngine,
)
from modules.ai_evolution_engine.core.evolution_events import (
    EvolutionEvent,
    EvolutionEventBus,
)
from modules.ai_evolution_engine.core.evolution_kernel import EvolutionKernel
from modules.ai_evolution_engine.core.evolution_manager import (
    EvolutionManager,
    ManagerState,
)
from modules.ai_evolution_engine.core.evolution_memory import EvolutionMemory
from modules.ai_evolution_engine.core.evolution_pipeline import (
    AnalysisResult,
    EvolutionPipeline,
    EvolutionReport,
)
from modules.ai_evolution_engine.core.evolution_registry import EvolutionRegistry
from modules.ai_evolution_engine.core.evolution_state import EvolutionState

__all__ = [
    "AnalysisResult",
    "EngineResult",
    "EvolutionContext",
    "EvolutionEngine",
    "EvolutionEvent",
    "EvolutionEventBus",
    "EvolutionKernel",
    "EvolutionManager",
    "EvolutionMemory",
    "EvolutionPipeline",
    "EvolutionRegistry",
    "EvolutionReport",
    "EvolutionState",
    "ManagerState",
]
