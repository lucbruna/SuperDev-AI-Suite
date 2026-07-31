"""Factory Events - Event-driven messaging for factory operations."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class FactoryEventType(Enum):
    PROJECT_CREATED = "project_created"
    PHASE_STARTED = "phase_started"
    PHASE_COMPLETED = "phase_completed"
    ARTIFACT_GENERATED = "artifact_generated"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    ERROR_OCCURRED = "error_occurred"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"


@dataclass
class FactoryEvent:
    event_id: str
    event_type: FactoryEventType
    project_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class FactoryEventBus:
    def __init__(self):
        self.events: List[FactoryEvent] = []
        self.subscribers: Dict[FactoryEventType, List[Callable]] = {}

    def publish(self, event_type: FactoryEventType, project_id: str, data: Dict[str, Any] = None) -> FactoryEvent:
        event_id = hashlib.sha256(f"{event_type.value}{project_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        event = FactoryEvent(event_id=event_id, event_type=event_type, project_id=project_id, data=data or {})
        self.events.append(event)
        for handler in self.subscribers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass
        return event

    def subscribe(self, event_type: FactoryEventType, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def get_events(self, event_type: FactoryEventType = None, project_id: str = None, limit: int = 100) -> List[FactoryEvent]:
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if project_id:
            events = [e for e in events if e.project_id == project_id]
        return events[-limit:]

    def count(self) -> int:
        return len(self.events)
