"""Audit trail for governance actions."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class AuditTrail:
    """Immutable log of who did what, when and with what result."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def record(self, actor: str, action: str, resource: str,
               status: str = "ok", detail: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {"actor": actor, "action": action, "resource": resource,
                 "status": status, "detail": detail or {},
                 "ts": datetime.now().isoformat()}
        self._entries.append(entry)
        return entry

    def search(self, actor: str | None = None, action: str | None = None,
               resource: str | None = None) -> list[dict[str, Any]]:
        return [entry for entry in self._entries
                if (actor is None or entry["actor"] == actor)
                and (action is None or entry["action"] == action)
                and (resource is None or entry["resource"] == resource)]

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return list(self._entries[-limit:])

    def counts_by_action(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry["action"]] = counts.get(entry["action"], 0) + 1
        return counts

    def count(self) -> int:
        return len(self._entries)
