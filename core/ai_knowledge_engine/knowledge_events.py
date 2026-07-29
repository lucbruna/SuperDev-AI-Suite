from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class EventType(Enum):
    KNOWLEDGE_CREATED = "knowledge.created"
    KNOWLEDGE_VALIDATED = "knowledge.validated"
    KNOWLEDGE_DEPRECATED = "knowledge.deprecated"
    KNOWLEDGE_UPDATED = "knowledge.updated"
    KNOWLEDGE_REJECTED = "knowledge.rejected"
    RESEARCH_STARTED = "research.started"
    RESEARCH_COMPLETED = "research.completed"
    RESEARCH_FAILED = "research.failed"
    DOCUMENT_ANALYZED = "document.analyzed"
    DOCUMENT_PROCESSED = "document.processed"
    EMBEDDING_CREATED = "embedding.created"
    VECTOR_INDEXED = "vector.indexed"
    VECTOR_SEARCHED = "vector.searched"
    REASONING_STARTED = "reasoning.started"
    REASONING_COMPLETED = "reasoning.completed"
    HYPOTHESIS_FORMED = "hypothesis.formed"
    HYPOTHESIS_TESTED = "hypothesis.tested"
    LEARNING_APPLIED = "learning.applied"
    FEEDBACK_RECEIVED = "feedback.received"
    GRAPH_UPDATED = "graph.updated"
    GRAPH_NODE_ADDED = "graph.node_added"
    GRAPH_EDGE_ADDED = "graph.edge_added"
    VALIDATION_STARTED = "validation.started"
    VALIDATION_COMPLETED = "validation.completed"
    CONFIDENCE_CHANGED = "confidence.changed"
    CLASSIFICATION_CHANGED = "classification.changed"
    KNOWLEDGE_SYNCED = "knowledge.synced"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


@dataclass
class KnowledgeEvent:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    priority: int = 0
    correlation_id: Optional[str] = None


EventHandler = Union[Callable[[KnowledgeEvent], None], Callable[[KnowledgeEvent], Awaitable[None]]]


class KnowledgeEventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_history: List[KnowledgeEvent] = []
        self._max_history = 1000
        self._event_counts: Dict[EventType, int] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_global(self, handler: EventHandler) -> None:
        self._global_handlers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> bool:
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            return True
        return False

    async def publish(self, event: KnowledgeEvent) -> None:
        await self._queue.put(event)
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1

    async def publish_nowait(self, event: KnowledgeEvent) -> None:
        await self._process_event(event)

    async def start_processor(self) -> None:
        if self._processor_task is not None:
            return
        self._processor_task = asyncio.create_task(self._event_processor_loop())

    async def stop_processor(self) -> None:
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
            self._processor_task = None

    async def _event_processor_loop(self) -> None:
        while True:
            try:
                event = await self._queue.get()
                await self._process_event(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Knowledge event processor error: {e}")

    async def _process_event(self, event: KnowledgeEvent) -> None:
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        handlers = list(self._handlers.get(event.event_type, []))
        handlers.extend(self._global_handlers)
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[KnowledgeEvent]:
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
        return self._event_history[-limit:]

    def get_event_count(self, event_type: EventType) -> int:
        return self._event_counts.get(event_type, 0)

    def get_all_counts(self) -> Dict[str, int]:
        return {k.value: v for k, v in self._event_counts.items()}