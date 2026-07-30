from __future__ import annotations

import logging
import uuid
from typing import Any


class TestCase:
    """Represents a project test case."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.status: str = "pending"


class TestManager:
    """Manages project test cases."""

    def __init__(self) -> None:
        self._tests: dict[str, TestCase] = {}
        self._log = logging.getLogger("superdev.project.tests")

    def create(self, name: str, project_id: str) -> TestCase:
        t = TestCase(name=name, project_id=project_id)
        self._tests[t.id] = t
        return t

    def get(self, test_id: str) -> TestCase | None:
        return self._tests.get(test_id)

    def update_status(self, test_id: str, status: str) -> None:
        t = self._tests.get(test_id)
        if t:
            t.status = status

    def list_by_project(self, project_id: str) -> list[TestCase]:
        return [t for t in self._tests.values() if t.project_id == project_id]
