from __future__ import annotations

import logging
from typing import Any

from .project_models import Project, ProjectStatus


class ProjectManager:
    """Manages project state transitions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.project.manager")

    def activate(self, project: Project) -> None:
        project.status = ProjectStatus.ACTIVE
        self._log.info("Project %s activated", project.id)

    def pause(self, project: Project) -> None:
        project.status = ProjectStatus.PAUSED
        self._log.info("Project %s paused", project.id)

    def complete(self, project: Project) -> None:
        project.status = ProjectStatus.COMPLETED
        self._log.info("Project %s completed", project.id)

    def archive(self, project: Project) -> None:
        project.status = ProjectStatus.ARCHIVED
        self._log.info("Project %s archived", project.id)
