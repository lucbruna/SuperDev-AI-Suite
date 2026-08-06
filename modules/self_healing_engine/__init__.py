"""Self-Healing Engine module for the SuperDev AI Suite.

Detects, diagnoses, plans and executes controlled fixes, keeping the
platform healthy and reducing manual maintenance work.
"""
from __future__ import annotations

from modules.self_healing_engine.version import VERSION, __version__
from modules.self_healing_engine.core import (
    EngineResult,
    HealingContext,
    HealingEngine,
    HealingEvent,
    HealingEventBus,
    HealingKernel,
    HealingManager,
    HealingMemory,
    HealingMemoryError,
    HealingPipeline,
    HealingRegistry,
    HealingRegistryError,
    HealingState,
    KernelStatus,
    ManagerState,
    PipelineResult,
    PipelineStepResult,
)

__all__ = [
    "__version__",
    "VERSION",
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
