"""Release manager."""

from __future__ import annotations

import time
from typing import Any


class ReleaseManager:
    def __init__(self) -> None:
        self._releases: list[dict[str, Any]] = []

    def create(self, version: str, project: str, artifacts: list[str] = None) -> dict[str, Any]:
        release = {
            "version": version,
            "project": project,
            "artifacts": artifacts or [],
            "status": "created",
            "created_at": time.time(),
        }
        self._releases.append(release)
        return release

    def promote(self, version: str, environment: str) -> bool:
        for r in self._releases:
            if r["version"] == version:
                r["status"] = f"promoted_to_{environment}"
                return True
        return False

    def list_all(self, project: str = "", limit: int = 20) -> list[dict[str, Any]]:
        releases = self._releases
        if project:
            releases = [r for r in releases if r["project"] == project]
        return releases[-limit:]

    def count(self) -> int:
        return len(self._releases)
