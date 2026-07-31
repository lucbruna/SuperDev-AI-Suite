from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class ProjectEngine:
    """Renders the project management page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project")
        self._context = context or FrontendContext()
        self._projects: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "project",
            "count": len(self._projects),
            "projects": self.list(),
        }

    def list(self) -> list[dict[str, Any]]:
        return [
            {"project_id": project_id, **project}
            for project_id, project in self._projects.items()
        ]

    def open(self, project_id: str) -> dict[str, Any]:
        project = self._projects.get(project_id)
        if project is None:
            raise KeyError(f"unknown project: {project_id}")
        return {"project_id": project_id, **project}

    def create(self, data: dict[str, Any]) -> str:
        project_id = f"project-{len(self._projects) + 1}"
        self._projects[project_id] = {
            "name": data.get("name", project_id),
            "created_at": time.time(),
            "status": "active",
        }
        return project_id

    def delete(self, project_id: str) -> bool:
        return self._projects.pop(project_id, None) is not None
