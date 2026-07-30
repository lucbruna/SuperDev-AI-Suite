from __future__ import annotations

import logging
import uuid
from typing import Any


class Artifact:
    """Represents a project artifact."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.path: str = ""
        self.size: int = 0


class ArtifactManager:
    """Manages project artifacts."""

    def __init__(self) -> None:
        self._artifacts: dict[str, Artifact] = {}
        self._log = logging.getLogger("superdev.project.artifacts")

    def create(self, name: str, project_id: str) -> Artifact:
        a = Artifact(name=name, project_id=project_id)
        self._artifacts[a.id] = a
        return a

    def get(self, artifact_id: str) -> Artifact | None:
        return self._artifacts.get(artifact_id)

    def list_by_project(self, project_id: str) -> list[Artifact]:
        return [a for a in self._artifacts.values() if a.project_id == project_id]
