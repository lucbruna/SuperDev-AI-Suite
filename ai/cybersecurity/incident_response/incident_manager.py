"""
Incident Lifecycle Management
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Severity(Enum):
    P1 = "critical"
    P2 = "high"
    P3 = "medium"
    P4 = "low"


class IncidentStatus(Enum):
    DETECTED = "detected"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"


@dataclass
class Incident:
    incident_id: str
    title: str
    severity: Severity = Severity.P3
    status: IncidentStatus = IncidentStatus.DETECTED
    description: str = ""
    assignee: str = ""
    reporter: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
    sla_hours: int = 24
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class IncidentManager:
    def __init__(self):
        self.incidents: dict[str, Incident] = {}

    def create_incident(self, title: str, severity: Severity = Severity.P3, description: str = "", reporter: str = "") -> Incident:
        incident_id = hashlib.sha256(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        sla_map = {Severity.P1: 4, Severity.P2: 24, Severity.P3: 72, Severity.P4: 168}
        incident = Incident(incident_id=incident_id, title=title, severity=severity, description=description, reporter=reporter, sla_hours=sla_map.get(severity, 72))
        self.incidents[incident_id] = incident
        return incident

    def update_status(self, incident_id: str, status: IncidentStatus) -> bool:
        incident = self.incidents.get(incident_id)
        if incident:
            incident.status = status
            incident.updated_at = datetime.now()
            if status == IncidentStatus.CLOSED:
                incident.resolved_at = datetime.now()
            return True
        return False

    def assign(self, incident_id: str, assignee: str) -> bool:
        incident = self.incidents.get(incident_id)
        if incident:
            incident.assignee = assignee
            incident.updated_at = datetime.now()
            return True
        return False

    def get_incident(self, incident_id: str) -> Incident | None:
        return self.incidents.get(incident_id)

    def get_open_incidents(self) -> list[Incident]:
        return [i for i in self.incidents.values() if i.status not in (IncidentStatus.CLOSED, IncidentStatus.RECOVERED)]

    def get_by_severity(self, severity: Severity) -> list[Incident]:
        return [i for i in self.incidents.values() if i.severity == severity]

    def get_by_assignee(self, assignee: str) -> list[Incident]:
        return [i for i in self.incidents.values() if i.assignee == assignee]

    def check_sla(self, incident_id: str) -> dict[str, Any]:
        incident = self.incidents.get(incident_id)
        if not incident:
            return {"breached": False}
        elapsed = (datetime.now() - incident.created_at).total_seconds() / 3600
        return {"breached": elapsed > incident.sla_hours, "elapsed_hours": round(elapsed, 1), "sla_hours": incident.sla_hours}

    def count(self) -> int:
        return len(self.incidents)
