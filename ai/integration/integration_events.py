"""
Integration Events - Event-driven integration messaging
"""
import contextlib
import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(Enum):
    INTEGRATION_CREATED = "integration_created"
    INTEGRATION_UPDATED = "integration_updated"
    INTEGRATION_DELETED = "integration_deleted"
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    DATA_RECEIVED = "data_received"
    DATA_SENT = "data_sent"
    ERROR_OCCURRED = "error_occurred"
    STATUS_CHANGED = "status_changed"


@dataclass
class IntegrationEvent:
    event_id: str
    event_type: EventType
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class IntegrationEvents:
    def __init__(self):
        self.events: list[IntegrationEvent] = []
        self.subscribers: dict[EventType, list[Callable]] = {}
        self.event_history: dict[str, list[IntegrationEvent]] = {}

    def publish(self, event_type: EventType, source: str, data: dict[str, Any] = None, **kwargs) -> IntegrationEvent:
        event = IntegrationEvent(event_id=hashlib.sha256(f"{event_type.value}{source}{datetime.now().isoformat()}".encode()).hexdigest()[:16], event_type=event_type, source=source, data=data or {}, metadata=kwargs)
        self.events.append(event)
        self.event_history.setdefault(source, []).append(event)
        self._notify_subscribers(event)
        return event

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable) -> bool:
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                return True
            except ValueError:
                pass
        return False

    def _notify_subscribers(self, event: IntegrationEvent) -> None:
        for callback in self.subscribers.get(event.event_type, []):
            with contextlib.suppress(Exception):
                callback(event)

    def get_events(self, event_type: EventType = None, source: str = None) -> list[IntegrationEvent]:
        results = self.events
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if source:
            results = [e for e in results if e.source == source]
        return results

    def get_source_history(self, source: str) -> list[IntegrationEvent]:
        return self.event_history.get(source, [])

    def get_recent(self, limit: int = 10) -> list[IntegrationEvent]:
        return self.events[-limit:]

    def clear(self) -> None:
        self.events.clear()
        self.event_history.clear()

    def count(self) -> int:
        return len(self.events)
