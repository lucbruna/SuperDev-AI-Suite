from __future__ import annotations

import logging
import time
import uuid
from typing import Any


class ApprovalStage:
    """CI/CD approval stage — manual or automatic gating."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.approval")
        self._decisions: dict[str, dict[str, Any]] = {}

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        """Open an approval request. Auto-approves when ``auto_approve`` is set."""
        stage_id = f"approval-{uuid.uuid4().hex[:8]}"
        auto = bool(config.get("auto_approve", False))
        record = {
            "stage_id": stage_id,
            "status": "approved" if auto else "pending",
            "requested_at": time.time(),
            "decision": None,
        }
        self._decisions[stage_id] = record
        return {"ok": auto, "status": record["status"], "stage_id": stage_id}

    def approve(self, stage_id: str, user: str) -> bool:
        record = self._decisions.get(stage_id)
        if record is None or record["status"] != "pending":
            return False
        record["status"] = "approved"
        record["decision"] = "approved"
        record["approved_by"] = user
        record["decided_at"] = time.time()
        return True

    def reject(self, stage_id: str, user: str, reason: str) -> bool:
        record = self._decisions.get(stage_id)
        if record is None or record["status"] != "pending":
            return False
        record["status"] = "rejected"
        record["decision"] = "rejected"
        record["rejected_by"] = user
        record["reason"] = reason
        record["decided_at"] = time.time()
        return True
