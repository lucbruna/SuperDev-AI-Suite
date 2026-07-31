"""Member activity log."""

from __future__ import annotations

import time
from typing import Any


class MemberActivity:
    """Records actions performed by a member."""

    def __init__(self, member_id: str, max_entries: int = 200) -> None:
        self.member_id = member_id
        self.max_entries = max_entries
        self._entries: list[dict[str, Any]] = []

    def record(self, action: str, target: str = "",
               details: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {"action": action, "target": target,
                 "details": dict(details or {}), "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        return entry

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._entries[-limit:])

    def count(self) -> int:
        return len(self._entries)


class ActivityLog:
    """Activity log registry per member."""

    def __init__(self) -> None:
        self._logs: dict[str, MemberActivity] = {}

    def for_member(self, member_id: str) -> MemberActivity:
        log = self._logs.get(member_id)
        if log is None:
            log = MemberActivity(member_id)
            self._logs[member_id] = log
        return log
