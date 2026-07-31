"""Software Factory Engine - Core engine for autonomous software creation."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FactoryPhase(Enum):
    IDEATION = "ideation"
    REQUIREMENTS = "requirements"
    ARCHITECTURE = "architecture"
    GENERATION = "generation"
    TESTING = "testing"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"


class ProjectStatus(Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    REVIEW = "review"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class SoftwareProject:
    project_id: str
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    phase: FactoryPhase = FactoryPhase.IDEATION
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class SoftwareFactoryEngine:
    def __init__(self):
        self.projects: dict[str, SoftwareProject] = {}
        self.phase_log: list[dict[str, Any]] = []

    def create_project(self, name: str, description: str = "", owner: str = "") -> SoftwareProject:
        project_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        project = SoftwareProject(project_id=project_id, name=name, description=description, owner=owner)
        self.projects[project_id] = project
        self._log_phase(project_id, FactoryPhase.IDEATION, "created")
        return project

    def advance_phase(self, project_id: str) -> bool:
        project = self.projects.get(project_id)
        if not project:
            return False
        phases = list(FactoryPhase)
        idx = phases.index(project.phase)
        if idx < len(phases) - 1:
            project.phase = phases[idx + 1]
            project.updated_at = datetime.now()
            self._log_phase(project_id, project.phase, "advanced")
            return True
        return False

    def set_status(self, project_id: str, status: ProjectStatus) -> bool:
        project = self.projects.get(project_id)
        if project:
            project.status = status
            project.updated_at = datetime.now()
            return True
        return False

    def get_project(self, project_id: str) -> SoftwareProject | None:
        return self.projects.get(project_id)

    def list_projects(self, status: ProjectStatus = None) -> list[SoftwareProject]:
        if status:
            return [p for p in self.projects.values() if p.status == status]
        return list(self.projects.values())

    def count(self) -> int:
        return len(self.projects)

    def _log_phase(self, project_id: str, phase: FactoryPhase, action: str):
        self.phase_log.append(
            {"project_id": project_id, "phase": phase.value, "action": action, "timestamp": datetime.now().isoformat()}
        )
