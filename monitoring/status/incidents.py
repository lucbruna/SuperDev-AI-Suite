import uuid
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Incident:
    id: str
    title: str
    severity: str  # critical, major, minor
    services: List[str]
    status: str  # investigating, identified, monitoring, resolved
    created_at: float
    resolved_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "services": self.services,
            "status": self.status,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
        }


class IncidentManager:
    def __init__(self) -> None:
        self._incidents: Dict[str, Incident] = {}

    def create(self, title: str, severity: str = "minor", services: Optional[List[str]] = None) -> Incident:
        incident_id = str(uuid.uuid4())
        incident = Incident(
            id=incident_id,
            title=title,
            severity=severity,
            services=services or [],
            status="investigating",
            created_at=time.time(),
        )
        self._incidents[incident_id] = incident
        return incident

    def update(self, id: str, status: str) -> Optional[Incident]:
        incident = self._incidents.get(id)
        if incident is None:
            return None
        incident.status = status
        return incident

    def resolve(self, id: str) -> Optional[Incident]:
        incident = self._incidents.get(id)
        if incident is None:
            return None
        incident.status = "resolved"
        incident.resolved_at = time.time()
        return incident

    def list(self) -> List[Incident]:
        return list(self._incidents.values())

    def get(self, id: str) -> Optional[Incident]:
        return self._incidents.get(id)
