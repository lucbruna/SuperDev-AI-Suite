"""Project lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import (ProjectRecord, ProjectStatus,
                                                WorkspaceRecord)
from collaboration.collaboration_protocols import new_id
from collaboration.projects.project_activity import ProjectActivity
from collaboration.projects.project_metrics import ProjectMetrics
from collaboration.projects.project_settings import ProjectSettings
from collaboration.projects.project_structure import ProjectStructure


class ProjectManager:
    """CRUD for projects plus per-project structure/settings/metrics."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
        self._settings: dict[str, ProjectSettings] = {}
        self._activity: dict[str, ProjectActivity] = {}
        self._metrics: dict[str, ProjectMetrics] = {}
        self._structure: dict[str, ProjectStructure] = {}

    def create(self, workspace_id: str, name: str,
               owner_id: str = "", description: str = "",
               status: ProjectStatus = ProjectStatus.PLANNING,
               **settings: Any) -> ProjectRecord:
        project = ProjectRecord(project_id=new_id("prj"),
                                workspace_id=workspace_id, name=name,
                                owner_id=owner_id, description=description,
                                status=status, progress=0.0)
        if self.registry is not None:
            self.registry.register_project(project.project_id, project)
        self._settings[project.project_id] = ProjectSettings(
            project.project_id, initial=settings or None)
        self._activity[project.project_id] = ProjectActivity(
            project.project_id)
        self._metrics[project.project_id] = ProjectMetrics(project.project_id)
        self._structure[project.project_id] = ProjectStructure(
            project.project_id)
        return project

    def get(self, project_id: str) -> ProjectRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_project(project_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_projects()

    def remove(self, project_id: str) -> bool:
        removed = False
        if self.registry is not None:
            removed = self.registry.remove_project(project_id)
        if removed:
            self._settings.pop(project_id, None)
            self._activity.pop(project_id, None)
            self._metrics.pop(project_id, None)
            self._structure.pop(project_id, None)
        return removed

    def settings(self, project_id: str) -> ProjectSettings:
        settings = self._settings.get(project_id)
        if settings is None:
            raise KeyError(f"unknown project: {project_id}")
        return settings

    def activity(self, project_id: str) -> ProjectActivity:
        activity = self._activity.get(project_id)
        if activity is None:
            raise KeyError(f"unknown project: {project_id}")
        return activity

    def metrics(self, project_id: str) -> ProjectMetrics:
        metrics = self._metrics.get(project_id)
        if metrics is None:
            raise KeyError(f"unknown project: {project_id}")
        return metrics

    def structure(self, project_id: str) -> ProjectStructure:
        structure = self._structure.get(project_id)
        if structure is None:
            raise KeyError(f"unknown project: {project_id}")
        return structure

    def update_progress(self, project_id: str, progress: float) -> ProjectRecord | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.progress = max(0.0, min(100.0, progress))
        return project

    def update_status(self, project_id: str,
                      status: ProjectStatus) -> ProjectRecord | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.status = status
        return project

    def by_workspace(self, workspace_id: str) -> list[ProjectRecord]:
        if self.registry is None:
            return []
        projects = []
        for project_id in self.registry.list_projects():
            project = self.registry.get_project(project_id)
            if project is not None and project.workspace_id == workspace_id:
                projects.append(project)
        return projects

    def count(self) -> int:
        return len(self._settings)
