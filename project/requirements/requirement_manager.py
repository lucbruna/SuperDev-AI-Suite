from __future__ import annotations

import logging
import uuid
from enum import Enum
from typing import Any


class RequirementPriority(Enum):
    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"
    COULD_HAVE = "could_have"
    WONT_HAVE = "wont_have"


class Requirement:
    """Represents a project requirement."""

    def __init__(self, title: str, project_id: str, priority: RequirementPriority = RequirementPriority.MUST_HAVE) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.project_id = project_id
        self.priority = priority
        self.description: str = ""
        self.acceptance_criteria: list[str] = []
        self.status: str = "open"


class RequirementManager:
    """Manages project requirements."""

    def __init__(self) -> None:
        self._requirements: dict[str, Requirement] = {}
        self._log = logging.getLogger("superdev.project.requirements")

    def create(self, title: str, project_id: str, priority: RequirementPriority = RequirementPriority.MUST_HAVE) -> Requirement:
        req = Requirement(title=title, project_id=project_id, priority=priority)
        self._requirements[req.id] = req
        self._log.info("Created requirement %s", req.id)
        return req

    def get(self, req_id: str) -> Requirement | None:
        return self._requirements.get(req_id)

    def list_by_project(self, project_id: str) -> list[Requirement]:
        return [r for r in self._requirements.values() if r.project_id == project_id]

    def update_status(self, req_id: str, status: str) -> None:
        req = self._requirements.get(req_id)
        if req:
            req.status = status
