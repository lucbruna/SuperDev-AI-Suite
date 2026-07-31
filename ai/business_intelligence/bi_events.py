"""BI Events — Event-driven messaging for BI operations."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class BIEventType(Enum):
    DATA_INGESTED = "data_ingested"
    KPI_UPDATED = "kpi_updated"
    INSIGHT_GENERATED = "insight_generated"
    PREDICTION_CREATED = "prediction_created"
    DECISION_MADE = "decision_made"
    ALERT_TRIGGERED = "alert_triggered"
    REPORT_GENERATED = "report_generated"
    ANOMALY_DETECTED = "anomaly_detected"


@dataclass
class BIEvent:
    event_id: str
    event_type: BIEventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class BIEventBus:
    def __init__(self):
        self.events: List[BIEvent] = []
        self.subscribers: Dict[BIEventType, List[Callable]] = {}

    def publish(self, event_type: BIEventType, source: str, data: Dict[str, Any] = None) -> BIEvent:
        event_id = hashlib.sha256(f"{event_type.value}{source}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        event = BIEvent(event_id=event_id, event_type=event_type, source=source, data=data or {})
        self.events.append(event)
        for handler in self.subscribers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass
        return event

    def subscribe(self, event_type: BIEventType, handler: Callable) -> None:
        self.subscribers.setdefault(event_type, []).append(handler)

    def get_events(self, event_type: BIEventType = None, source: str = None, limit: int = 100) -> List[BIEvent]:
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]
        return events[-limit:]

    def count(self) -> int:
        return len(self.events)
