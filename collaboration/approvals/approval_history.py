"""Approval history."""

from __future__ import annotations

import time
from typing import Any

from collaboration.collaboration_models import ApprovalStatus


class ApprovalHistory:
    """Records each step decision for an approval request."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def record(self, step: int, label: str, decider: str,
               approved: bool, reason: str = "") -> None:
        self._entries.append({
            "step": step, "label": label, "decider": decider,
            "approved": approved, "reason": reason,
            "timestamp": time.time(),
        })

    def entries(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def last(self) -> dict[str, Any] | None:
        return self._entries[-1] if self._entries else None

    def all_approved(self) -> bool:
        return bool(self._entries) and \
            all(e["approved"] for e in self._entries)

    def status_for(self) -> ApprovalStatus:
        if not self._entries:
            return ApprovalStatus.PENDING
        if any(not e["approved"] for e in self._entries):
            return ApprovalStatus.REJECTED
        return ApprovalStatus.APPROVED

    def count(self) -> int:
        return len(self._entries)
