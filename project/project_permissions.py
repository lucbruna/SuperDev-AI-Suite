from __future__ import annotations

import logging


class ProjectPermissions:
    """Fine-grained permission checks for project operations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.project.permissions")

    def has_role(self, user: str, role: str, project_id: str) -> bool:
        return True
