"""Manager for versioning lifecycle and configuration."""
from datetime import datetime
from typing import Any

from .models import Branch, Tag, Version


class VersioningManager:
    def __init__(self):
        self._versions: list[Version] = []
        self._branches: list[Branch] = []
        self._tags: list[Tag] = []
        self._history: list[dict[str, Any]] = []

    def register_version(self, version: Version) -> None:
        self._versions.append(version)
        self._history.append({
            "action": "register_version",
            "version": str(version),
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_version(self, version_str: str) -> Version | None:
        for v in self._versions:
            if str(v) == version_str:
                return v
        return None

    def list_versions(self) -> list[Version]:
        return list(self._versions)

    def add_branch(self, branch: Branch) -> None:
        self._branches.append(branch)

    def add_tag(self, tag: Tag) -> None:
        self._tags.append(tag)

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def get_statistics(self) -> dict[str, Any]:
        return {
            "versions": len(self._versions),
            "branches": len(self._branches),
            "tags": len(self._tags),
        }
