from __future__ import annotations

import logging
from typing import Any

from .project_models import Project


class ProjectRuntime:
    """Runtime context for active project execution."""

    def __init__(self) -> None:
        self._active: dict[str, dict[str, Any]] = {}
        self._log = logging.getLogger("superdev.project.runtime")

    def start(self, project_id: str) -> None:
        self._active[project_id] = {"status": "running"}
        self._log.info("Runtime started for %s", project_id)

    def stop(self, project_id: str) -> None:
        self._active.pop(project_id, None)

    def is_running(self, project_id: str) -> bool:
        return project_id in self._active
