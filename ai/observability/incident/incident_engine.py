"""Incident engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class IncidentEngine:
    def __init__(self) -> None:
        self._incidents: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def create_incident(self, title: str, severity: str = "medium", description: str = "") -> Dict[str, Any]:
        import uuid
        incident_id = str(uuid.uuid4())[:8]
        incident = {"id": incident_id, "title": title, "severity": severity, "description": description, "status": "open", "created_at": time.time(), "timeline": []}
        self._incidents[incident_id] = incident
        return incident
    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        return self._incidents.get(incident_id)
    def list_incidents(self, status: str = "") -> List[Dict[str, Any]]:
        incidents = list(self._incidents.values())
        if status:
            incidents = [i for i in incidents if i["status"] == status]
        return incidents
    def resolve_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        incident = self._incidents.get(incident_id)
        if incident:
            incident["status"] = "resolved"
            incident["resolved_at"] = time.time()
            return incident
        return None
    def get_status(self) -> Dict[str, Any]:
        open_count = sum(1 for i in self._incidents.values() if i["status"] == "open")
        return {"running": self._started, "total": len(self._incidents), "open": open_count}
