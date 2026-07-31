from __future__ import annotations

import logging
from typing import Any


class ProjectTimeline:
    """Project milestones and timeline."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project.timeline")
        self._milestones: dict[str, list[dict[str, Any]]] = {}

    def render(self, project_id: str) -> dict[str, Any]:
        return {"project_id": project_id, "milestones": self.milestones(project_id)}

    def milestones(self, project_id: str) -> list[dict[str, Any]]:
        return list(self._milestones.get(project_id, []))

    def add(self, project_id: str, milestone: dict[str, Any]) -> bool:
        self._milestones.setdefault(project_id, []).append(milestone)
        return True
