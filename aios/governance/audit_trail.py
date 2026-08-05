"""AuditTrail: append-only deterministic record of governance decisions."""
from __future__ import annotations

from typing import Any, Optional

DECISION_LEVELS = ("allow", "deny", "pending", "approved", "rejected")


class AuditTrail:
    """Sequential audit entries with filtering and summary helpers."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._seq = 0

    def record(
        self,
        subject: str,
        action: str,
        resource: str,
        decision: str,
        detail: str = "",
        **extra: Any,
    ) -> dict[str, Any]:
        self._seq += 1
        entry = {
            "seq": self._seq,
            "subject": subject,
            "action": action,
            "resource": resource,
            "decision": decision,
            "detail": detail,
            **extra,
        }
        self._entries.append(entry)
        return dict(entry)

    def entries(self) -> list[dict[str, Any]]:
        return [dict(entry) for entry in self._entries]

    def filter(
        self,
        subject: str | None = None,
        action: str | None = None,
        resource: str | None = None,
        decision: str | None = None,
    ) -> list[dict[str, Any]]:
        out = []
        for entry in self._entries:
            if subject is not None and entry["subject"] != subject:
                continue
            if action is not None and entry["action"] != action:
                continue
            if resource is not None and entry["resource"] != resource:
                continue
            if decision is not None and entry["decision"] != decision:
                continue
            out.append(dict(entry))
        return out

    def summary(self) -> dict[str, Any]:
        counts = {level: 0 for level in DECISION_LEVELS}
        for entry in self._entries:
            level = entry["decision"]
            counts[level] = counts.get(level, 0) + 1
        return {"total": len(self._entries), "by_decision": counts}
