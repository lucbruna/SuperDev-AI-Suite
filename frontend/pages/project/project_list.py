from __future__ import annotations

import logging
from typing import Any


class ProjectList:
    """Project inventory with filtering and sorting."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project.list")
        self._projects: list[dict[str, Any]] = []

    def render(self) -> dict[str, Any]:
        return {"projects": list(self._projects), "count": len(self._projects)}

    def query(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        results = list(self._projects)
        for key, value in filters.items():
            if key in ("status", "owner"):
                results = [p for p in results if p.get(key) == value]
        return results

    def sort(self, projects: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
        return sorted(projects, key=lambda p: str(p.get(key, "")))
