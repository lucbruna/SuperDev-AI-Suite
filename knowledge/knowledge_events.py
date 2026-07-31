from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable


class KnowledgeEventType(str, Enum):
    MEMORY_STORED = "knowledge.memory_stored"
    MEMORY_RECALLED = "knowledge.memory_recalled"
    MEMORY_PRUNED = "knowledge.memory_pruned"
    DOCUMENT_ADDED = "knowledge.document_added"
    DOCUMENT_UPDATED = "knowledge.document_updated"
    EMBEDDING_CREATED = "knowledge.embedding_created"
    INDEX_UPDATED = "knowledge.index_updated"
    SEARCH_EXECUTED = "knowledge.search_executed"
    GRAPH_UPDATED = "knowledge.graph_updated"
    ERROR = "knowledge.error"


class KnowledgeEvents:
    """Emits and subscribes to knowledge lifecycle events."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.events")
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

    def emit(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(event_type=event_type, payload=payload or {})
            except Exception as exc:  # noqa: BLE001 - listener isolation
                self._log.warning("listener failed for %s: %s", event_type, exc)

    def on(self, event_type: str, listener: Callable[..., Any]) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def off(self, event_type: str, listener: Callable[..., Any]) -> None:
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
            except ValueError:
                pass

    def once(self, event_type: str, listener: Callable[..., Any]) -> None:
        def _wrapper(**kwargs: Any) -> None:
            self.off(event_type, _wrapper)
            listener(**kwargs)

        self.on(event_type, _wrapper)

    def listener_count(self, event_type: str) -> int:
        return len(self._listeners.get(event_type, []))
