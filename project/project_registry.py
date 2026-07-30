from __future__ import annotations

import logging
from typing import Any

from .project_models import Project


class ProjectRegistry:
    """In-memory registry for active projects."""

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._log = logging.getLogger("superdev.project.registry")

    def register(self, project: Project) -> None:
        self._projects[project.id] = project
        self._log.debug("Registered %s", project.id)

    def unregister(self, project_id: str) -> None:
        self._projects.pop(project_id, None)

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    def list_active(self) -> list[Project]:
        return list(self._projects.values())
