"""Incident manager."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class IncidentManager:
    def __init__(self) -> None:
        self._assignments: Dict[str, str] = {}
        self._updates: List[Dict[str, Any]] = []
    def assign(self, incident_id: str, assignee: str) -> Dict[str, Any]:
        self._assignments[incident_id] = assignee
        entry = {"incident_id": incident_id, "assignee": assignee, "action": "assigned", "timestamp": time.time()}
        self._updates.append(entry)
        return entry
    def add_update(self, incident_id: str, message: str, author: str = "") -> Dict[str, Any]:
        entry = {"incident_id": incident_id, "message": message, "author": author, "timestamp": time.time()}
        self._updates.append(entry)
        return entry
    def get_assignee(self, incident_id: str) -> Optional[str]:
        return self._assignments.get(incident_id)
    def get_updates(self, incident_id: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._updates
        if incident_id:
            results = [u for u in results if u["incident_id"] == incident_id]
        return results[-limit:]
    def reassign(self, incident_id: str, new_assignee: str) -> Optional[Dict[str, Any]]:
        if incident_id in self._assignments:
            old = self._assignments[incident_id]
            self._assignments[incident_id] = new_assignee
            return {"incident_id": incident_id, "from": old, "to": new_assignee, "timestamp": time.time()}
        return None
