"""Audit logging for integration operations."""

from __future__ import annotations

import time
from typing import Any


class AuditLog:
    """Records auditable integration operations."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def record(self, actor: str, action: str, resource: str,
               details: dict[str, Any] | None = None) -> None:
        self._entries.append({
            "actor": actor,
            "action": action,
            "resource": resource,
            "details": details or {},
            "timestamp": time.time(),
        })

    def entries(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._entries[-limit:])

    def filter(self, actor: str | None = None, action: str | None = None) -> list[dict[str, Any]]:
        result = self._entries
        if actor:
            result = [e for e in result if e["actor"] == actor]
        if action:
            result = [e for e in result if e["action"] == action]
        return list(result)

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()
