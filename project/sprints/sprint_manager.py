from __future__ import annotations

import logging
import uuid
from typing import Any


class Sprint:
    """Represents a project sprint."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.status: str = "planning"
        self.tasks: list[str] = []


class SprintManager:
    """Manages project sprints."""

    def __init__(self) -> None:
        self._sprints: dict[str, Sprint] = {}
        self._log = logging.getLogger("superdev.project.sprints")

    def create(self, name: str, project_id: str) -> Sprint:
        sprint = Sprint(name=name, project_id=project_id)
        self._sprints[sprint.id] = sprint
        self._log.info("Created sprint %s", sprint.id)
        return sprint

    def get(self, sprint_id: str) -> Sprint | None:
        return self._sprints.get(sprint_id)

    def list_by_project(self, project_id: str) -> list[Sprint]:
        return [s for s in self._sprints.values() if s.project_id == project_id]

    def add_task(self, sprint_id: str, task_id: str) -> None:
        sprint = self._sprints.get(sprint_id)
        if sprint:
            sprint.tasks.append(task_id)

    def start(self, sprint_id: str) -> None:
        sprint = self._sprints.get(sprint_id)
        if sprint:
            sprint.status = "active"

    def complete(self, sprint_id: str) -> None:
        sprint = self._sprints.get(sprint_id)
        if sprint:
            sprint.status = "completed"
