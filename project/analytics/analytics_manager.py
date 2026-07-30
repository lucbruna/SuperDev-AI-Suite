from __future__ import annotations

import logging
from typing import Any


class AnalyticsManager:
    """Tracks project analytics."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []
        self._log = logging.getLogger("superdev.project.analytics")

    def track(self, event: str, project_id: str, data: dict[str, Any] | None = None) -> None:
        entry = {"event": event, "project_id": project_id, "data": data or {}}
        self._events.append(entry)

    def query(self, project_id: str) -> list[dict[str, Any]]:
        return [e for e in self._events if e["project_id"] == project_id]
