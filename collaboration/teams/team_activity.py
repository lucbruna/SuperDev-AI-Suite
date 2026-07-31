"""Team activity tracking."""

from __future__ import annotations

import time
from typing import Any


class TeamActivity:
    """Records events that happened inside a team."""

    def __init__(self, team_id: str, max_entries: int = 300) -> None:
        self.team_id = team_id
        self.max_entries = max_entries
        self._entries: list[dict[str, Any]] = []

    def record(self, action: str, actor_id: str,
               details: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {"action": action, "actor_id": actor_id,
                 "details": dict(details or {}), "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        return entry

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._entries[-limit:])

    def filter(self, action: str | None = None) -> list[dict[str, Any]]:
        if action is None:
            return list(self._entries)
        return [e for e in self._entries if e["action"] == action]

    def count(self) -> int:
        return len(self._entries)
