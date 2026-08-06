"""Self-Healing Engine core package: context, pipeline, engine, kernel, manager.

All components are deterministic: no wall clock, no network, no LLM.
"""
from __future__ import annotations

from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.core.healing_engine import (
    EngineResult,
    HealingEngine,
)
from modules.self_healing_engine.core.healing_events import (
    HealingEvent,
    HealingEventBus,
)
from modules.self_healing_engine.core.healing_kernel import (
    HealingKernel,
    KernelStatus,
)
from modules.self_healing_engine.core.healing_manager import (
    HealingManager,
    ManagerState,
)
from modules.self_healing_engine.core.healing_memory import (
    HealingMemory,
    HealingMemoryError,
)
from modules.self_healing_engine.core.healing_pipeline import (
    HealingPipeline,
    PipelineResult,
    PipelineStepResult,
)
from modules.self_healing_engine.core.healing_registry import (
    HealingRegistry,
    HealingRegistryError,
)
from modules.self_healing_engine.core.healing_state import HealingState

__all__ = [
    "EngineResult",
    "HealingContext",
    "HealingEngine",
    "HealingEvent",
    "HealingEventBus",
    "HealingKernel",
    "HealingManager",
    "HealingMemory",
    "HealingMemoryError",
    "HealingPipeline",
    "HealingRegistry",
    "HealingRegistryError",
    "HealingState",
    "KernelStatus",
    "ManagerState",
    "PipelineResult",
    "PipelineStepResult",
]
