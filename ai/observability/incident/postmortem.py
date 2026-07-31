"""Postmortem management."""
from __future__ import annotations

import time
from typing import Any


class PostmortemManager:
    def __init__(self) -> None:
        self._postmortems: dict[str, dict[str, Any]] = {}
    def create(self, incident_id: str, summary: str = "", root_cause: str = "", action_items: list[str] = None) -> dict[str, Any]:
        pm = {"incident_id": incident_id, "summary": summary, "root_cause": root_cause, "action_items": action_items or [], "created_at": time.time(), "status": "draft"}
        self._postmortems[incident_id] = pm
        return pm
    def get(self, incident_id: str) -> dict[str, Any]:
        return self._postmortems.get(incident_id, {})
    def update(self, incident_id: str, **kwargs: Any) -> dict[str, Any]:
        pm = self._postmortems.get(incident_id)
        if pm:
            pm.update(kwargs)
            return pm
        return {}
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._postmortems.values())
    def add_action_item(self, incident_id: str, item: str) -> bool:
        pm = self._postmortems.get(incident_id)
        if pm:
            pm["action_items"].append(item)
            return True
        return False
    def remove(self, incident_id: str) -> bool:
        if incident_id in self._postmortems:
            del self._postmortems[incident_id]
            return True
        return False
