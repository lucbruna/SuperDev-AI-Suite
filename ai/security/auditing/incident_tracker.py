"""Incident tracking."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time, uuid

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Incident:
    def __init__(self, title: str, severity: IncidentSeverity, description: str = "") -> None:
        self.incident_id = str(uuid.uuid4())[:8]
        self.title = title
        self.severity = severity
        self.description = description
        self.status = IncidentStatus.OPEN
        self.created_at = time.time()
        self.updates: List[Dict[str, Any]] = []
        self.assignee = ""

class IncidentTracker:
    def __init__(self) -> None:
        self._incidents: Dict[str, Incident] = {}
    def create_incident(self, title: str, severity: IncidentSeverity, description: str = "") -> Incident:
        inc = Incident(title, severity, description)
        self._incidents[inc.incident_id] = inc
        return inc
    def update_status(self, incident_id: str, status: IncidentStatus, note: str = "") -> bool:
        inc = self._incidents.get(incident_id)
        if inc:
            inc.status = status
            inc.updates.append({"status": status.value, "note": note, "timestamp": time.time()})
            return True
        return False
    def assign(self, incident_id: str, assignee: str) -> bool:
        inc = self._incidents.get(incident_id)
        if inc:
            inc.assignee = assignee
            return True
        return False
    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        inc = self._incidents.get(incident_id)
        if inc:
            return {"id": inc.incident_id, "title": inc.title, "severity": inc.severity.value, "status": inc.status.value, "assignee": inc.assignee, "updates_count": len(inc.updates), "created_at": inc.created_at}
        return None
    def list_incidents(self, status: Optional[IncidentStatus] = None, severity: Optional[IncidentSeverity] = None) -> List[str]:
        results = self._incidents
        if status:
            results = {k: v for k, v in results.items() if v.status == status}
        if severity:
            results = {k: v for k, v in results.items() if v.severity == severity}
        return list(results.keys())
    def stats(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for inc in self._incidents.values():
            counts[inc.status.value] = counts.get(inc.status.value, 0) + 1
        return counts
