from __future__ import annotations

from typing import Any

from .api_constants import API_VERSION, API_NAME, API_DESCRIPTION


class APIVersion:
    """API version information and management."""

    def __init__(self) -> None:
        self._version = API_VERSION
        self._name = API_NAME
        self._description = API_DESCRIPTION
        self._changelog: list[dict[str, Any]] = []

    @property
    def version(self) -> str:
        return self._version

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def bump_major(self) -> str:
        parts = self._version.split(".")
        self._version = f"{int(parts[0]) + 1}.0.0"
        return self._version

    def bump_minor(self) -> str:
        parts = self._version.split(".")
        self._version = f"{parts[0]}.{int(parts[1]) + 1}.0"
        return self._version

    def bump_patch(self) -> str:
        parts = self._version.split(".")
        self._version = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        return self._version

    def add_changelog_entry(self, version: str, change: str) -> None:
        self._changelog.append({"version": version, "change": change})

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self._version,
            "name": self._name,
            "description": self._description,
            "changelog": list(self._changelog),
        }
