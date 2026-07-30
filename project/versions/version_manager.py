from __future__ import annotations

import logging
import uuid
from typing import Any


class Version:
    """Represents a project version."""

    def __init__(self, label: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.label = label
        self.project_id = project_id
        self.tags: list[str] = []


class VersionManager:
    """Manages project versions."""

    def __init__(self) -> None:
        self._versions: dict[str, Version] = {}
        self._log = logging.getLogger("superdev.project.versions")

    def create(self, label: str, project_id: str) -> Version:
        v = Version(label=label, project_id=project_id)
        self._versions[v.id] = v
        return v

    def get(self, version_id: str) -> Version | None:
        return self._versions.get(version_id)

    def list_by_project(self, project_id: str) -> list[Version]:
        return [v for v in self._versions.values() if v.project_id == project_id]
