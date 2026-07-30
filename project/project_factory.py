from __future__ import annotations

import time
from typing import Any

from .project_models import Project, ProjectStatus


class ProjectFactory:
    """Creates new Project instances."""

    @staticmethod
    def create(name: str, owner: str = "", **kwargs: Any) -> Project:
        now = time.time()
        return Project(
            name=name,
            owner=owner,
            status=ProjectStatus.DRAFT,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
