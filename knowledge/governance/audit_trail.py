from __future__ import annotations

import logging
from typing import Any


class AuditTrail:
    """Records governance-relevant actions for compliance."""

    def __init__(self, max_entries: int = 500) -> None:
        self._log = logging.getLogger("superdev.knowledge.governance.audit_trail")
        self.max_entries = max(1, max_entries)
        self._entries: list[dict[str, Any]] = []

    def record(self, action: str, actor: str = "system", **details: Any) -> None:
        self._entries.append({"action": action, "actor": actor, **details})
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]

    def list(self, action: str | None = None) -> list[dict[str, Any]]:
        if action is None:
            return list(self._entries)
        return [entry for entry in self._entries if entry.get("action") == action]

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()
