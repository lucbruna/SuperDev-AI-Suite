from __future__ import annotations

import logging
from typing import Any


class ProjectDetails:
    """Project info and activity feed."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project.details")
        self._projects: dict[str, dict[str, Any]] = {}
        self._activity: dict[str, list[dict[str, Any]]] = {}

    def render(self, project_id: str) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "info": self.info(project_id),
            "activity": self.activity(project_id),
        }

    def info(self, project_id: str) -> dict[str, Any]:
        project = self._projects.get(project_id)
        if project is None:
            raise KeyError(f"unknown project: {project_id}")
        return dict(project)

    def activity(self, project_id: str, limit: int = 20) -> list[dict[str, Any]]:
        return self._activity.get(project_id, [])[-limit:]
