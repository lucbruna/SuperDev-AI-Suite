"""Version control."""
from __future__ import annotations

from typing import Any


class VersionControl:
    def __init__(self) -> None:
        self._versions: dict[str, dict[str, Any]] = {}
    def tag(self, version: str, commit: str, message: str = "") -> dict[str, Any]:
        tag = {"version": version, "commit": commit, "message": message}
        self._versions[version] = tag
        return tag
    def get(self, version: str) -> dict[str, Any]:
        return self._versions.get(version, {"error": "not_found"})
    def list_tags(self) -> list[dict[str, Any]]:
        return list(self._versions.values())
    def latest(self) -> str:
        return list(self._versions.keys())[-1] if self._versions else ""
    def count(self) -> int:
        return len(self._versions)
