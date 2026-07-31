"""Release management."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ReleaseManager:
    def __init__(self) -> None:
        self._releases: List[Dict[str, Any]] = []
    def create_release(self, version: str, project: str, notes: str = "") -> Dict[str, Any]:
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
    def list_releases(self, project: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        releases = self._releases
        if project:
            releases = [r for r in releases if r["project"] == project]
        return releases[-limit:]
    def count(self) -> int:
        return len(self._releases)
