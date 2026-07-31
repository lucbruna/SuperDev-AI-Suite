from __future__ import annotations

import logging
from typing import Any


class ProjectSettings:
    """Project configuration and permissions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project.settings")
        self._projects: dict[str, dict[str, Any]] = {}

    def render(self, project_id: str) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "settings": self._projects.get(project_id, {}),
            "permissions": self.permissions(project_id),
        }

    def update(self, project_id: str, data: dict[str, Any]) -> bool:
        self._projects.setdefault(project_id, {}).update(data)
        return True

    def permissions(self, project_id: str) -> dict[str, Any]:
        return {
            "viewers": True,
            "editors": True,
            "admins": True,
            "public": False,
        }
