from __future__ import annotations

import logging
from typing import Any

from .project_models import Project


class ProjectSecurity:
    """Security checks for project operations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.project.security")

    def can_create(self, user: str, project: Project) -> bool:
        """Allow creation by default. Override for custom policies."""
        return True

    def can_delete(self, user: str, project: Project) -> bool:
        return user in (project.owner,)

    def can_modify(self, user: str, project: Project) -> bool:
        return user == project.owner
