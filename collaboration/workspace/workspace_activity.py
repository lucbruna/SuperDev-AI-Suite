"""Workspace activity tracking."""

from __future__ import annotations

import time
from typing import Any


class WorkspaceActivity:
    """Records and queries events that happened inside a workspace."""

    def __init__(self, workspace_id: str,
                 max_entries: int = 500) -> None:
        self.workspace_id = workspace_id
        self.max_entries = max_entries
        self._entries: list[dict[str, Any]] = []

    def record(self, action: str, actor_id: str,
               details: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {"action": action, "actor_id": actor_id,
                 "details": dict(details or {}),
                 "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        return entry

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._entries[-limit:])

    def filter(self, action: str | None = None,
               actor_id: str | None = None) -> list[dict[str, Any]]:
        results = self._entries
        if action is not None:
            results = [e for e in results if e["action"] == action]
        if actor_id is not None:
            results = [e for e in results if e["actor_id"] == actor_id]
        return list(results)

    def count(self) -> int:
        return len(self._entries)
