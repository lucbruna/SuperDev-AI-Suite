"""Build stage."""

from __future__ import annotations

import time
from typing import Any


class BuildStage:
    def __init__(self) -> None:
        self._builds: list[dict[str, Any]] = []

    def build(self, project: str, branch: str = "main", commit: str = "") -> dict[str, Any]:
        import uuid

        build_id = str(uuid.uuid4())[:8]
        build = {
            "build_id": build_id,
            "project": project,
            "branch": branch,
            "commit": commit,
            "status": "success",
            "artifacts": [f"{project}.tar.gz"],
            "duration_seconds": 120.0,
            "timestamp": time.time(),
        }
        self._builds.append(build)
        return build

    def get_build(self, build_id: str) -> dict[str, Any]:
        for b in self._builds:
            if b["build_id"] == build_id:
                return b
        return {"error": "not_found"}

    def list_builds(self, project: str = "", limit: int = 20) -> list[dict[str, Any]]:
        builds = self._builds
        if project:
            builds = [b for b in builds if b["project"] == project]
        return builds[-limit:]

    def count(self) -> int:
        return len(self._builds)
