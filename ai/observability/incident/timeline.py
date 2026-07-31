"""Incident timeline."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class IncidentTimeline:
    def __init__(self) -> None:
        self._timelines: Dict[str, List[Dict[str, Any]]] = {}
    def add_event(self, incident_id: str, event_type: str, description: str, author: str = "") -> Dict[str, Any]:
        event = {"type": event_type, "description": description, "author": author, "timestamp": time.time()}
        self._timelines.setdefault(incident_id, []).append(event)
        return event
    def get_timeline(self, incident_id: str) -> List[Dict[str, Any]]:
        return list(self._timelines.get(incident_id, []))
    def get_duration(self, incident_id: str) -> float:
        events = self._timelines.get(incident_id, [])
        if len(events) < 2:
            return 0.0
        return events[-1]["timestamp"] - events[0]["timestamp"]
    def list_incidents(self) -> List[str]:
        return list(self._timelines.keys())
    def clear_timeline(self, incident_id: str) -> int:
        n = len(self._timelines.get(incident_id, []))
        self._timelines.pop(incident_id, None)
        return n
