"""Audit Bridge — structured audit trail for sensitive operations."""
from __future__ import annotations

import time
from typing import Any


class AuditBridge:
    """Appends immutable audit entries (bounded ring buffer)."""

    def __init__(self, limit: int = 500) -> None:
        self._entries: list[dict[str, Any]] = []
        self._limit = limit

    def record(self, actor: str, action: str, *, target: str = "",
               result: str = "ok", detail: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {
            "ts": round(time.time(), 3),
            "actor": actor,
            "action": action,
            "target": target,
            "result": result,
            "detail": dict(detail or {}),
        }
        self._entries.append(entry)
        if len(self._entries) > self._limit:
            self._entries = self._entries[-self._limit:]
        return {"recorded": len(self._entries), "entry_id": len(self._entries)}

    def entries(self, *, limit: int = 50, actor: str | None = None) -> dict[str, Any]:
        items = [e for e in self._entries if actor is None or e["actor"] == actor]
        return {"entries": items[-limit:], "count": len(items)}


_audit_bridge: AuditBridge | None = None


def get_audit_bridge() -> AuditBridge:
    global _audit_bridge
    if _audit_bridge is None:
        _audit_bridge = AuditBridge()
    return _audit_bridge
