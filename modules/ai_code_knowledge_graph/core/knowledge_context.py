"""Knowledge context — the object threaded through the pipeline.

Carries configuration, the event bus, state tracker, registry, memory,
session and per-run statistics so every component shares one coherent view
of the current scan/build.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.core.knowledge_events import EventBus
from modules.ai_code_knowledge_graph.core.knowledge_memory import KnowledgeMemory
from modules.ai_code_knowledge_graph.core.knowledge_registry import KnowledgeRegistry, default_registry
from modules.ai_code_knowledge_graph.core.knowledge_session import KnowledgeSession, SessionManager
from modules.ai_code_knowledge_graph.core.knowledge_state import KnowledgeStateTracker

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class KnowledgeContext:
    """Shared context for one knowledge pipeline run."""

    config: KnowledgeConfig
    # Shared process-wide registry: components registered by any phase
    # (parsers, analyzers, ...) are automatically visible to every context.
    registry: KnowledgeRegistry = field(default_factory=default_registry)
    bus: EventBus = field(default_factory=EventBus)
    state: KnowledgeStateTracker = field(default_factory=KnowledgeStateTracker)
    memory: KnowledgeMemory = field(default_factory=KnowledgeMemory)
    sessions: SessionManager = field(default_factory=SessionManager)
    stats: dict[str, Any] = field(default_factory=dict)
    cancel_requested: bool = False
    started_at: float = field(default_factory=time.time)

    def create_session(self, meta: dict[str, Any] | None = None) -> KnowledgeSession:
        return self.sessions.create(project_root=self.config.scanner.project_root, meta=meta)

    def request_cancel(self) -> None:
        self.cancel_requested = True
        self.bus.publish("pipeline.cancelled", {})

    @property
    def cancelled(self) -> bool:
        return self.cancel_requested

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        self.bus.publish(event_type, payload)

    def record(self, key: str, value: Any) -> None:
        self.stats[key] = value

    def elapsed_seconds(self) -> float:
        return round(time.time() - self.started_at, 3)
