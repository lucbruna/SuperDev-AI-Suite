"""Core package for the Autonomous Developer module.

Domain models, the event bus, the state machine, the component registry,
working memory, sessions, the shared context and the runtime orchestrator
that wires them together.
"""
from __future__ import annotations

from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.events import DeveloperEvent, EventBus
from modules.autonomous_developer.core.exceptions import (
    DeveloperError,
    ExecutionError,
    GenerationError,
    PermissionDeniedError,
    PlanningError,
    SecurityError,
    ValidationError,
)
from modules.autonomous_developer.core.memory import DeveloperMemory
from modules.autonomous_developer.core.models import (
    FileChange,
    ReviewVerdict,
    Task,
    TaskPlan,
)
from modules.autonomous_developer.core.registry import (
    DeveloperRegistry,
    default_registry,
    register_decorator,
)
from modules.autonomous_developer.core.runtime import (
    DeveloperRuntime,
    build_runtime,
)
from modules.autonomous_developer.core.session import DeveloperSession, SessionManager
from modules.autonomous_developer.core.state import (
    DeveloperState,
    DeveloperStateTracker,
    StateTransition,
)

__all__ = [
    "DeveloperContext",
    "DeveloperError",
    "DeveloperEvent",
    "DeveloperMemory",
    "DeveloperRegistry",
    "DeveloperRuntime",
    "DeveloperSession",
    "DeveloperState",
    "DeveloperStateTracker",
    "EventBus",
    "ExecutionError",
    "FileChange",
    "GenerationError",
    "PermissionDeniedError",
    "PlanningError",
    "ReviewVerdict",
    "SecurityError",
    "SessionManager",
    "StateTransition",
    "Task",
    "TaskPlan",
    "ValidationError",
    "build_runtime",
    "default_registry",
    "register_decorator",
]
