"""Events for the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from enterprise_knowledge.knowledge_logger import get_logger

_Listener = Callable[[dict[str, Any]], None]


class EnterpriseKnowledgeEventType(Enum):
    NODE_CREATED = "ek.node.created"
    NODE_UPDATED = "ek.node.updated"
    NODE_REMOVED = "ek.node.removed"
    RELATIONSHIP_CREATED = "ek.relationship.created"
    RELATIONSHIP_REMOVED = "ek.relationship.removed"
    DOCUMENT_INDEXED = "ek.document.indexed"
    DOCUMENT_REMOVED = "ek.document.removed"
    MEMORY_STORED = "ek.memory.stored"
    MEMORY_RECALLED = "ek.memory.recalled"
    SEARCH_EXECUTED = "ek.search.executed"
    EXTRACTION_COMPLETED = "ek.extraction.completed"
    REASONING_COMPLETED = "ek.reasoning.completed"
    INDEX_UPDATED = "ek.index.updated"
    ACCESS_DENIED = "ek.access.denied"
    GOVERNANCE_ACTION = "ek.governance.action"


class EnterpriseKnowledgeEvents:
    """Thread-safe pub/sub event bus with listener isolation."""

    def __init__(self) -> None:
        self._log = get_logger("events")
        self._listeners: dict[EnterpriseKnowledgeEventType,
                              list[_Listener]] = {}

    def on(self, event_type: EnterpriseKnowledgeEventType,
           listener: _Listener) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def once(self, event_type: EnterpriseKnowledgeEventType,
             listener: _Listener) -> None:
        def _wrapper(payload: dict[str, Any]) -> None:
            self.off(event_type, _wrapper)
            listener(payload)

        self.on(event_type, _wrapper)

    def off(self, event_type: EnterpriseKnowledgeEventType,
            listener: _Listener) -> None:
        listeners = self._listeners.get(event_type)
        if listeners is not None and listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type: EnterpriseKnowledgeEventType,
                payload: dict[str, Any]) -> None:
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(payload)
            except Exception:  # noqa: BLE001 - listener isolation
                self._log.warning(
                    "listener failed for %s: %s", event_type.value,
                    listener)
