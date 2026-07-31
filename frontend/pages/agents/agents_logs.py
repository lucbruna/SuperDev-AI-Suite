from __future__ import annotations

import json
import logging
from typing import Any


class AgentsLogs:
    """Searchable agent execution logs."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents.logs")
        self._entries: list[dict[str, Any]] = []

    def render(self) -> dict[str, Any]:
        return {"entries": list(self._entries), "count": len(self._entries)}

    def search(self, query: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        results = [
            entry for entry in self._entries if query.lower() in str(entry).lower()
        ]
        for key, value in (filters or {}).items():
            results = [r for r in results if r.get(key) == value]
        return results

    def export(self, entries: list[dict[str, Any]]) -> str:
        return json.dumps(entries, indent=2, default=str)
