"""AIOS Audit Service — append-only audit trail.

Records who did what, when, on which resource and with what outcome.
Queryable by actor/action/resource.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class AuditService:
    """In-memory append-only audit log."""

    def __init__(self, max_entries: int = 10_000) -> None:
        self._entries: list[dict[str, Any]] = []
        self._max = max_entries

    def record(
        self,
        actor: str,
        action: str,
        resource: str,
        outcome: str = "success",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "audit_id": f"aud-{uuid.uuid4().hex[:10]}",
            "actor": actor,
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "details": details or {},
            "timestamp": time.time(),
        }
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry

    def query(
        self,
        actor: str | None = None,
        action: str | None = None,
        resource: str | None = None,
        outcome: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        matches = []
        for entry in reversed(self._entries):
            if actor is not None and entry["actor"] != actor:
                continue
            if action is not None and entry["action"] != action:
                continue
            if resource is not None and entry["resource"] != resource:
                continue
            if outcome is not None and entry["outcome"] != outcome:
                continue
            matches.append(entry)
            if len(matches) >= limit:
                break
        return matches

    def clear(self) -> None:
        self._entries.clear()

    def snapshot(self) -> dict[str, Any]:
        return {"entries": len(self._entries), "max": self._max}
