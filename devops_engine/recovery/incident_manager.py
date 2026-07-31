"""Incident management for recovery (Volume 37, Fase 5)."""

from __future__ import annotations

from devops_engine.devops_models import Incident, IncidentStatus, Severity
from devops_engine.devops_protocols import new_id, now


class IncidentManager:
    """Drives incidents through the full lifecycle."""

    def __init__(self) -> None:
        self._incidents: dict[str, Incident] = {}

    def raise_incident(self, title: str,
                       severity: Severity = Severity.WARNING,
                       source: str = "") -> Incident:
        incident = Incident(
            incident_id=new_id("incident"),
            title=title,
            severity=severity,
            status=IncidentStatus.OPEN,
            source=source,
            detected_at=now(),
        )
        self._incidents[incident.incident_id] = incident
        return incident

    def investigate(self, incident_id: str) -> bool:
        incident = self._incidents.get(incident_id)
        if incident is None:
            return False
        incident.status = IncidentStatus.INVESTIGATING
        return True

    def mitigate(self, incident_id: str) -> bool:
        incident = self._incidents.get(incident_id)
        if incident is None:
            return False
        incident.status = IncidentStatus.MITIGATED
        return True

    def resolve(self, incident_id: str) -> bool:
        incident = self._incidents.get(incident_id)
        if incident is None:
            return False
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = now()
        return True

    def get(self, incident_id: str) -> Incident | None:
        return self._incidents.get(incident_id)

    def list_open(self) -> list[Incident]:
        return [incident for incident in self._incidents.values()
                if incident.status != IncidentStatus.RESOLVED]

    def count(self) -> int:
        return len(self._incidents)
