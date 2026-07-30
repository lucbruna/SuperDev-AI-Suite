from __future__ import annotations

import logging
import uuid
from typing import Any


class Release:
    """Represents a project release."""

    def __init__(self, version: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.version = version
        self.project_id = project_id
        self.status: str = "draft"
        self.notes: str = ""


class ReleaseManager:
    """Manages project releases."""

    def __init__(self) -> None:
        self._releases: dict[str, Release] = {}
        self._log = logging.getLogger("superdev.project.releases")

    def create(self, version: str, project_id: str) -> Release:
        release = Release(version=version, project_id=project_id)
        self._releases[release.id] = release
        return release

    def get(self, release_id: str) -> Release | None:
        return self._releases.get(release_id)

    def publish(self, release_id: str) -> None:
        release = self._releases.get(release_id)
        if release:
            release.status = "published"

    def list_by_project(self, project_id: str) -> list[Release]:
        return [r for r in self._releases.values() if r.project_id == project_id]
