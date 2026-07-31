from __future__ import annotations

import logging
from typing import Any


class ProjectDashboard:
    """Project-level dashboard with stats and charts."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project.dashboard")
        self._projects: dict[str, dict[str, Any]] = {}

    def render(self, project_id: str) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "stats": self.stats(project_id),
            "charts": self.charts(project_id),
        }

    def stats(self, project_id: str) -> dict[str, Any]:
        project = self._projects.get(project_id)
        if project is None:
            raise KeyError(f"unknown project: {project_id}")
        return {
            "commits": project.get("commits", 0),
            "agents": project.get("agents", 0),
            "workflows": project.get("workflows", 0),
            "deployments": project.get("deployments", 0),
        }

    def charts(self, project_id: str) -> list[dict[str, Any]]:
        return [
            {"kind": "line", "metric": "commits"},
            {"kind": "bar", "metric": "workflows"},
        ]
