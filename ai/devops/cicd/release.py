"""Release management."""
from __future__ import annotations

import time
from typing import Any


class ReleaseManager:
    def __init__(self) -> None:
        self._releases: list[dict[str, Any]] = []
    def create_release(self, version: str, project: str, notes: str = "") -> dict[str, Any]:
        release = {"version": version, "project": project, "notes": notes, "status": "created", "created_at": time.time()}
        self._releases.append(release)
        return release
    def approve(self, version: str) -> bool:
        for r in self._releases:
            if r["version"] == version:
                r["status"] = "approved"
                return True
        return False
    def release(self, version: str) -> bool:
        for r in self._releases:
            if r["version"] == version:
                r["status"] = "released"
                return True
        return False
    def list_releases(self, project: str = "", limit: int = 20) -> list[dict[str, Any]]:
        releases = self._releases
        if project:
            releases = [r for r in releases if r["project"] == project]
        return releases[-limit:]
    def count(self) -> int:
        return len(self._releases)
