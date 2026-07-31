"""
Security Events System
"""
from typing import Callable, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class SecurityEventData:
    event_id: str
    event_type: str
    severity: str
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class SecurityEvents:
    def __init__(self):
        self.events: List[SecurityEventData] = []
        self.listeners: Dict[str, List[Callable]] = {}
        self.max_events: int = 10000
        
    def emit(self, event_type: str, severity: str, source: str, data: Dict[str, Any] = None) -> SecurityEventData:
        event = SecurityEventData(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            severity=severity,
            source=source,
            data=data or {}
        )
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        self._dispatch(event)
        return event
        
    def on(self, event_type: str, callback: Callable) -> None:
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        
    def _dispatch(self, event: SecurityEventData) -> None:
        for callback in self.listeners.get(event.event_type, []):
            callback(event)
        for callback in self.listeners.get("*", []):
            callback(event)
            
    def get_recent(self, count: int = 100) -> List[SecurityEventData]:
        return self.events[-count:]
        
    def get_by_type(self, event_type: str) -> List[SecurityEventData]:
        return [e for e in self.events if e.event_type == event_type]
        
    def get_by_severity(self, severity: str) -> List[SecurityEventData]:
        return [e for e in self.events if e.severity == severity]
        
    def count(self) -> int:
        return len(self.events)
        
    def clear(self) -> None:
        self.events.clear()
