from __future__ import annotations

import logging
import time
from typing import Any


class ApprovalAudit:
    """Audit trail for approval actions."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._log = logging.getLogger("superdev.workflow.approvals.audit")

    def log(self, action: str, approval_id: str, details: dict[str, Any] | None = None) -> None:
        entry = {
            "action": action,
            "approval_id": approval_id,
            "timestamp": time.time(),
            "details": details or {},
        }
        self._entries.append(entry)
        self._log.debug("Audit: %s %s", action, approval_id)

    def get_history(self, approval_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["approval_id"] == approval_id]
