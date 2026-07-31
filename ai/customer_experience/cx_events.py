"""CX Events — Event-driven messaging for CX operations."""
import contextlib
import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CXEventType(Enum):
    CUSTOMER_CREATED = "customer_created"
    CUSTOMER_UPDATED = "customer_updated"
    INTERACTION_RECORDED = "interaction_recorded"
    TICKET_CREATED = "ticket_created"
    TICKET_RESOLVED = "ticket_resolved"
    LEAD_SCORED = "lead_scored"
    RECOMMENDATION_ACCEPTED = "recommendation_accepted"
    SENTIMENT_DETECTED = "sentiment_detected"
    LOYALTY_POINTS_EARNED = "loyalty_points_earned"
    JOURNEY_STAGE_ADVANCED = "journey_stage_advanced"


@dataclass
class CXEvent:
    event_id: str
    event_type: CXEventType
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class CXEventBus:
    def __init__(self):
        self.events: list[CXEvent] = []
        self.subscribers: dict[CXEventType, list[Callable]] = {}

    def publish(self, event_type: CXEventType, source: str, data: dict[str, Any] | None = None) -> CXEvent:
        event_id = hashlib.sha256(f"{event_type.value}{source}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        event = CXEvent(event_id=event_id, event_type=event_type, source=source, data=data or {})
        self.events.append(event)
        for handler in self.subscribers.get(event_type, []):
            with contextlib.suppress(Exception):
                handler(event)
        return event

    def subscribe(self, event_type: CXEventType, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def get_events(self, event_type: CXEventType | None = None, source: str | None = None, limit: int = 100) -> list[CXEvent]:
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]
        return events[-limit:]

    def count(self) -> int:
        return len(self.events)
