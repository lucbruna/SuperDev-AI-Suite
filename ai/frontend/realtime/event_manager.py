"""
Realtime Event Manager
"""

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Event:
    id: str
    type: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""


class EventManager:
    def __init__(self):
        self.events: list[Event] = []
        self.handlers: dict[str, list[Callable]] = {}
        self.max_history = 1000

    def emit(self, event_type: str, data: Any, source: str = "") -> Event:
        event = Event(id=str(uuid.uuid4()), type=event_type, data=data, source=source)
        self.events.append(event)
        if len(self.events) > self.max_history:
            self.events = self.events[-self.max_history :]
        self._dispatch(event)
        return event

    def on(self, event_type: str, handler: Callable) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def off(self, event_type: str, handler: Callable) -> None:
        if event_type in self.handlers:
            self.handlers[event_type] = [h for h in self.handlers[event_type] if h != handler]

    def _dispatch(self, event: Event) -> None:
        for handler in self.handlers.get(event.type, []):
            handler(event)
        for handler in self.handlers.get("*", []):
            handler(event)

    def get_recent(self, count: int = 10) -> list[Event]:
        return self.events[-count:]

    def clear(self) -> None:
        self.events.clear()

    def render(self) -> dict[str, Any]:
        return {"eventCount": len(self.events), "handlerCount": sum(len(h) for h in self.handlers.values())}
