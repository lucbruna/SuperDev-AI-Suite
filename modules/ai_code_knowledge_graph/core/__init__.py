"""Core package — engine, runtime, pipeline and shared infrastructure.

Public surface for the module's core: the engine facade, manager, runtime,
pipeline, event bus, state machine, registry, memory, sessions and
exceptions.
"""
from __future__ import annotations

from modules.ai_code_knowledge_graph.core.exceptions import (
    GraphBuildError,
    KnowledgeError,
    NotFoundError,
    ParseError,
    PermissionDeniedError,
    ScanError,
    StoreError,
)
from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_engine import KnowledgeEngine, get_engine
from modules.ai_code_knowledge_graph.core.knowledge_events import EventBus, KnowledgeEvent
from modules.ai_code_knowledge_graph.core.knowledge_kernel import KnowledgeKernel
from modules.ai_code_knowledge_graph.core.knowledge_manager import KnowledgeManager
from modules.ai_code_knowledge_graph.core.knowledge_memory import KnowledgeMemory
from modules.ai_code_knowledge_graph.core.knowledge_pipeline import KnowledgePipeline
from modules.ai_code_knowledge_graph.core.knowledge_registry import (
    KnowledgeRegistry,
    default_registry,
    register_decorator,
)
from modules.ai_code_knowledge_graph.core.knowledge_runtime import KnowledgeRuntime, build_runtime
from modules.ai_code_knowledge_graph.core.knowledge_session import KnowledgeSession, SessionManager
from modules.ai_code_knowledge_graph.core.knowledge_state import KnowledgeState, KnowledgeStateTracker, StateTransition

__all__ = [
    "EventBus",
    "GraphBuildError",
    "KnowledgeContext",
    "KnowledgeEngine",
    "KnowledgeError",
    "KnowledgeEvent",
    "KnowledgeKernel",
    "KnowledgeManager",
    "KnowledgeMemory",
    "KnowledgePipeline",
    "KnowledgeRegistry",
    "KnowledgeRuntime",
    "KnowledgeSession",
    "KnowledgeState",
    "KnowledgeStateTracker",
    "NotFoundError",
    "ParseError",
    "PermissionDeniedError",
    "ScanError",
    "SessionManager",
    "StateTransition",
    "StoreError",
    "build_runtime",
    "default_registry",
    "get_engine",
    "register_decorator",
]
