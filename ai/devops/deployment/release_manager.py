"""Release manager."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ReleaseManager:
    def __init__(self) -> None:
        self._releases: List[Dict[str, Any]] = []
    def create(self, version: str, project: str, artifacts: List[str] = None) -> Dict[str, Any]:
        release = {"version": version, "project": project, "artifacts": artifacts or [], "status": "created", "created_at": time.time()}
        self._releases.append(release)
        return release
    def promote(self, version: str, environment: str) -> bool:
        for r in self._releases:
            if r["version"] == version:
                r["status"] = f"promoted_to_{environment}"
                return True
        return False
    def list_all(self, project: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        releases = self._releases
        if project:
            releases = [r for r in releases if r["project"] == project]
        return releases[-limit:]
    def count(self) -> int:
        return len(self._releases)
