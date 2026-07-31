"""Incident response engine."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class IncidentPhase(Enum):
    DETECTION = "detection"
    ANALYSIS = "analysis"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    LESSONS_LEARNED = "lessons_learned"


class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class Incident:
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.LOW
    phase: IncidentPhase = IncidentPhase.DETECTION
    status: IncidentStatus = IncidentStatus.OPEN
    assignee: str = ""
    affected_assets: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    resolution: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Playbook:
    playbook_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    incident_type: str = ""
    phases: List[Dict[str, Any]] = field(default_factory=list)
    estimated_time_minutes: int = 60


class IncidentResponseEngine:
    def __init__(self):
        self._incidents: Dict[str, Incident] = {}
        self._playbooks: Dict[str, Playbook] = {}
        self._runbooks: Dict[str, List[str]] = {}

    def create_incident(self, title: str, description: str = "", severity: IncidentSeverity = IncidentSeverity.MEDIUM, assignee: str = "") -> Incident:
        inc = Incident(title=title, description=description, severity=severity, assignee=assignee)
        self._incidents[inc.incident_id] = inc
        return inc

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        return self._incidents.get(incident_id)

    def update_phase(self, incident_id: str, phase: IncidentPhase, note: str = "") -> bool:
        inc = self._incidents.get(incident_id)
        if not inc:
            return False
        inc.phase = phase
        inc.timeline.append({"phase": phase.value, "note": note, "timestamp": datetime.now().isoformat()})
        inc.updated_at = datetime.now()
        if phase == IncidentPhase.RECOVERY:
            inc.status = IncidentStatus.RESOLVED
        return True

    def add_to_timeline(self, incident_id: str, action: str, details: str = "") -> bool:
        inc = self._incidents.get(incident_id)
        if not inc:
            return False
        inc.timeline.append({"action": action, "details": details, "timestamp": datetime.now().isoformat()})
        inc.updated_at = datetime.now()
        return True

    def contain_incident(self, incident_id: str, actions: List[str]) -> bool:
        inc = self._incidents.get(incident_id)
        if not inc:
            return False
        inc.phase = IncidentPhase.CONTAINMENT
        inc.status = IncidentStatus.CONTAINED
        for action in actions:
            inc.timeline.append({"action": f"containment: {action}", "timestamp": datetime.now().isoformat()})
        inc.updated_at = datetime.now()
        return True

    def resolve_incident(self, incident_id: str, resolution: str = "") -> bool:
        inc = self._incidents.get(incident_id)
        if not inc:
            return False
        inc.resolution = resolution
        inc.status = IncidentStatus.RESOLVED
        inc.phase = IncidentPhase.RECOVERY
        inc.updated_at = datetime.now()
        return True

    def add_playbook(self, playbook: Playbook) -> None:
        self._playbooks[playbook.playbook_id] = playbook

    def get_playbook(self, incident_type: str) -> Optional[Playbook]:
        for pb in self._playbooks.values():
            if pb.incident_type == incident_type:
                return pb
        return None

    def get_incidents(self, severity: Optional[IncidentSeverity] = None, status: Optional[IncidentStatus] = None) -> List[Incident]:
        incidents = list(self._incidents.values())
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        if status:
            incidents = [i for i in incidents if i.status == status]
        return incidents

    def get_stats(self) -> dict:
        incidents = list(self._incidents.values())
        return {
            "total_incidents": len(incidents),
            "open": len([i for i in incidents if i.status == IncidentStatus.OPEN]),
            "in_progress": len([i for i in incidents if i.status == IncidentStatus.IN_PROGRESS]),
            "resolved": len([i for i in incidents if i.status == IncidentStatus.RESOLVED]),
            "critical": len([i for i in incidents if i.severity == IncidentSeverity.CRITICAL]),
            "playbooks": len(self._playbooks),
        }
