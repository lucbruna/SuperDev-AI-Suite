from __future__ import annotations

import logging
import uuid
from typing import Any


class Milestone:
    """Represents a project milestone."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.status: str = "pending"


class MilestoneManager:
    """Manages project milestones."""

    def __init__(self) -> None:
        self._milestones: dict[str, Milestone] = {}
        self._log = logging.getLogger("superdev.project.milestones")

    def create(self, name: str, project_id: str) -> Milestone:
        ms = Milestone(name=name, project_id=project_id)
        self._milestones[ms.id] = ms
        return ms

    def get(self, ms_id: str) -> Milestone | None:
        return self._milestones.get(ms_id)

    def complete(self, ms_id: str) -> None:
        ms = self._milestones.get(ms_id)
        if ms:
            ms.status = "completed"

    def list_by_project(self, project_id: str) -> list[Milestone]:
        return [m for m in self._milestones.values() if m.project_id == project_id]
