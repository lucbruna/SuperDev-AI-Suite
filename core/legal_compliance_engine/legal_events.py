"""
Legal Events - Event-driven communication for legal systems.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class EventType(Enum):
    CONTRACT_RECEIVED = "contract.received"
    CONTRACT_ANALYZED = "contract.analyzed"
    CONTRACT_APPROVED = "contract.approved"
    CONTRACT_REJECTED = "contract.rejected"
    CONTRACT_EXPIRING = "contract.expiring"
    CONTRACT_RISK_HIGH = "contract.risk_high"
    CONTRACT_AMENDED = "contract.amended"

    DOCUMENT_CLASSIFIED = "document.classified"
    DOCUMENT_ARCHIVED = "document.archived"
    DOCUMENT_EXPIRED = "document.expired"

    REGULATION_CHANGED = "regulation.changed"
    REGULATION_IMPACT = "regulation.impact_assessed"
    LAW_UPDATED = "regulation.law_updated"

    COMPLIANCE_CHECKED = "compliance.checked"
    COMPLIANCE_VIOLATION = "compliance.violation_detected"
    COMPLIANCE_PASSED = "compliance.passed"
    CONTROL_FAILED = "compliance.control_failed"

    RISK_ASSESSED = "risk.assessed"
    RISK_THRESHOLD_EXCEEDED = "risk.threshold_exceeded"
    RISK_MITIGATED = "risk.mitigated"

    AUDIT_STARTED = "audit.started"
    AUDIT_COMPLETED = "audit.completed"
    EVIDENCE_COLLECTED = "audit.evidence_collected"
    FINDING_ISSUED = "audit.finding_issued"

    POLICY_CREATED = "policy.created"
    POLICY_PUBLISHED = "policy.published"
    POLICY_ACKNOWLEDGED = "policy.acknowledged"
    POLICY_UPDATED = "policy.updated"

    CASE_OPENED = "litigation.case_opened"
    CASE_UPDATED = "litigation.case_updated"
    CASE_CLOSED = "litigation.case_closed"
    LITIGATION_DEADLINE = "litigation.deadline_approaching"
    LEGAL_PREDICTION = "litigation.prediction_made"

    LEGAL_HEALTH_CHANGED = "legal.health_changed"
    LEGAL_ALERT = "legal.alert"


@dataclass
class LegalEvent:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    correlation_id: Optional[str] = None
    priority: int = 0


EventHandler = Union[Callable[[LegalEvent], None], Callable[[LegalEvent], Awaitable[None]]]


class LegalEventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_history: List[LegalEvent] = []
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

    async def publish(self, event: LegalEvent) -> None:
        await self._queue.put(event)
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1

    async def publish_nowait(self, event: LegalEvent) -> None:
        await self._process_event(event)

    async def start_processor(self) -> None:
        if self._processor_task is not None:
            return
        self._processor_task = asyncio.create_task(self._event_processor_loop())

    async def stop_processor(self) -> None:
        if self._processor_task:
            self._processor_task.cancel()
            try: await self._processor_task
            except asyncio.CancelledError: pass
            self._processor_task = None

    async def _event_processor_loop(self) -> None:
        while True:
            try:
                event = await self._queue.get()
                await self._process_event(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processor error: {e}")

    async def _process_event(self, event: LegalEvent) -> None:
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

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[LegalEvent]:
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
        return self._event_history[-limit:]

    def get_event_count(self, event_type: EventType) -> int:
        return self._event_counts.get(event_type, 0)
