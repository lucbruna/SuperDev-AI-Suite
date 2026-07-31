"""Approval management."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ApprovalManager:
    def __init__(self) -> None:
        self._approvals: List[Dict[str, Any]] = []
    def request(self, pipeline: str, approver: str, environment: str = "production") -> Dict[str, Any]:
        import uuid
        approval_id = str(uuid.uuid4())[:8]
        approval = {"approval_id": approval_id, "pipeline": pipeline, "approver": approver, "environment": environment, "status": "pending", "requested_at": time.time()}
        self._approvals.append(approval)
        return approval
    def approve(self, approval_id: str) -> bool:
        for a in self._approvals:
            if a["approval_id"] == approval_id:
                a["status"] = "approved"
                a["approved_at"] = time.time()
                return True
        return False
    def reject(self, approval_id: str) -> bool:
        for a in self._approvals:
            if a["approval_id"] == approval_id:
                a["status"] = "rejected"
                return True
        return False
    def list_pending(self) -> List[Dict[str, Any]]:
        return [a for a in self._approvals if a["status"] == "pending"]
    def list_all(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._approvals[-limit:]
    def count(self) -> int:
        return len(self._approvals)
