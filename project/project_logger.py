from __future__ import annotations

import logging
import time
from typing import Any


class ProjectLogger:
    """Structured logger for project activity."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._log = logging.getLogger("superdev.project.logger")

    def log(self, action: str, project_id: str, details: dict[str, Any] | None = None) -> None:
        entry = {
            "action": action,
            "project_id": project_id,
            "timestamp": time.time(),
            "details": details or {},
        }
        self._entries.append(entry)
        self._log.debug("%s %s", action, project_id)

    def history(self, project_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["project_id"] == project_id]
