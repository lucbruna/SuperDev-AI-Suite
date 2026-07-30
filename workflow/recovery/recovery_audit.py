from __future__ import annotations

import logging
import time
from typing import Any


class RecoveryAudit:
    """Audit trail for recovery operations."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._log = logging.getLogger("superdev.workflow.recovery.audit")

    def log(self, action: str, plan_id: str, details: dict[str, Any] | None = None) -> None:
        entry = {
            "action": action,
            "plan_id": plan_id,
            "timestamp": time.time(),
            "details": details or {},
        }
        self._entries.append(entry)
        self._log.debug("Recovery audit: %s %s", action, plan_id)

    def get_history(self, plan_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["plan_id"] == plan_id]
