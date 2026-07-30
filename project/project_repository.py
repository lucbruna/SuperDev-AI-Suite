from __future__ import annotations

import logging
from typing import Any

from .project_models import Project


class ProjectRepository:
    """Persistence layer for project entities."""

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._log = logging.getLogger("superdev.project.repository")

    def save(self, project: Project) -> Project:
        self._projects[project.id] = project
        self._log.debug("Saved project %s", project.id)
        return project

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    def delete(self, project_id: str) -> None:
        self._projects.pop(project_id, None)

    def list_all(self) -> list[Project]:
        return list(self._projects.values())

    def find_by_name(self, name: str) -> list[Project]:
        return [p for p in self._projects.values() if name.lower() in p.name.lower()]
