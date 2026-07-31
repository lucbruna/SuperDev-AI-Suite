"""Timeline view."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class Timeline:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
    def add_event(self, event_id: str, timestamp: float, title: str, description: str = "", category: str = "general") -> Dict[str, Any]:
        event = {"event_id": event_id, "timestamp": timestamp, "title": title, "description": description, "category": category}
        self._events.append(event)
        self._events.sort(key=lambda e: e["timestamp"])
        return event
    def get_events(self, start: float = 0, end: float = float("inf"), category: str = "") -> List[Dict[str, Any]]:
        events = self._events
        if start > 0:
            events = [e for e in events if e["timestamp"] >= start]
        if end < float("inf"):
            events = [e for e in events if e["timestamp"] <= end]
        if category:
            events = [e for e in events if e["category"] == category]
        return events
    def remove_event(self, event_id: str) -> bool:
        original = len(self._events)
        self._events = [e for e in self._events if e["event_id"] != event_id]
        return len(self._events) < original
    def count(self) -> int:
        return len(self._events)
    def categories(self) -> List[str]:
        return list(set(e["category"] for e in self._events))
    def clear(self) -> int:
        n = len(self._events)
        self._events.clear()
        return n
