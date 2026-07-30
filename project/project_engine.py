from __future__ import annotations

import logging
import time
from typing import Any

from .project_models import Project, ProjectStatus
from .project_factory import ProjectFactory
from .project_manager import ProjectManager
from .project_registry import ProjectRegistry
from .project_repository import ProjectRepository
from .project_security import ProjectSecurity
from .project_events import ProjectEvents
from .project_metrics import ProjectMetrics
from .project_logger import ProjectLogger


class ProjectEngine:
    """Central engine orchestrating the project lifecycle."""

    def __init__(self) -> None:
        self._factory = ProjectFactory()
        self._manager = ProjectManager()
        self._registry = ProjectRegistry()
        self._repository = ProjectRepository()
        self._security = ProjectSecurity()
        self._events = ProjectEvents()
        self._metrics = ProjectMetrics()
        self._logger = ProjectLogger()
        self._log = logging.getLogger("superdev.project")

    def create_project(self, name: str, owner: str, **kwargs: Any) -> Project:
        project = self._factory.create(name=name, owner=owner, **kwargs)
        project = self._repository.save(project)
        self._registry.register(project)
        self._events.emit("project.created", project_id=project.id)
        self._metrics.record_creation()
        self._logger.log("created", project.id, {"name": name})
        self._log.info("Project created: %s (%s)", name, project.id)
        return project

    def get_project(self, project_id: str) -> Project | None:
        return self._repository.get(project_id)

    def list_projects(self) -> list[Project]:
        return self._repository.list_all()

    def update_project(self, project: Project) -> Project:
        project.updated_at = time.time()
        self._repository.save(project)
        self._events.emit("project.updated", project_id=project.id)
        self._logger.log("updated", project.id)
        return project

    def delete_project(self, project_id: str) -> None:
        self._repository.delete(project_id)
        self._registry.unregister(project_id)
        self._events.emit("project.deleted", project_id=project_id)
        self._logger.log("deleted", project_id)

    def change_status(self, project_id: str, status: ProjectStatus) -> None:
        project = self._repository.get(project_id)
        if project:
            project.status = status
            self.update_project(project)
            self._events.emit("project.status_changed", project_id=project_id, status=status.value)
