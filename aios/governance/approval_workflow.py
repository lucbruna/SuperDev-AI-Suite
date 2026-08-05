"""ApprovalWorkflow: deterministic multi-approver approval chains."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

APPROVAL_STATUSES = ("pending", "approved", "rejected")


@dataclass
class Approval:
    approval_id: str
    requested_by: str
    approvers: list[str]
    payload: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    approvals: list[str] = field(default_factory=list)
    rejections: dict[str, str] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)


class ApprovalWorkflow:
    """Tracks approvals; the chain approves when every approver approves."""

    def __init__(self) -> None:
        self._approvals: dict[str, Approval] = {}
        self._seq = 0

    def submit(
        self,
        requested_by: str,
        approvers: list[str],
        payload: dict[str, Any] | None = None,
    ) -> Approval:
        self._seq += 1
        approval = Approval(
            approval_id=f"appr-{self._seq:04d}",
            requested_by=requested_by,
            approvers=list(approvers),
            payload=dict(payload or {}),
        )
        approval.events.append({"seq": 1, "event": "submitted", "by": requested_by})
        self._approvals[approval.approval_id] = approval
        return approval

    def approve(self, approval_id: str, approver: str) -> bool:
        approval = self._require(approval_id)
        if approval.status != "pending":
            return False
        if approver not in approval.approvers:
            return False
        if approver not in approval.approvals:
            approval.approvals.append(approver)
            approval.events.append(
                {"seq": len(approval.events) + 1, "event": "approved", "by": approver}
            )
        if sorted(approval.approvers) == sorted(approval.approvals):
            approval.status = "approved"
            approval.events.append(
                {"seq": len(approval.events) + 1, "event": "finalized", "by": "system"}
            )
        return approval.status == "approved"

    def reject(self, approval_id: str, approver: str, reason: str = "") -> bool:
        approval = self._require(approval_id)
        if approval.status != "pending":
            return False
        approval.status = "rejected"
        approval.rejections[approver] = reason
        approval.events.append(
            {"seq": len(approval.events) + 1, "event": "rejected", "by": approver, "reason": reason}
        )
        return True

    def status(self, approval_id: str) -> Optional[str]:
        approval = self._approvals.get(approval_id)
        return approval.status if approval is not None else None

    def get(self, approval_id: str) -> Optional[Approval]:
        approval = self._approvals.get(approval_id)
        return approval

    def pending(self) -> list[str]:
        return sorted(
            approval_id
            for approval_id, approval in self._approvals.items()
            if approval.status == "pending"
        )

    def summary(self) -> dict[str, Any]:
        counts = {status: 0 for status in APPROVAL_STATUSES}
        for approval in self._approvals.values():
            counts[approval.status] = counts.get(approval.status, 0) + 1
        return {"total": len(self._approvals), "by_status": counts}

    def _require(self, approval_id: str) -> Approval:
        approval = self._approvals.get(approval_id)
        if approval is None:
            raise KeyError(f"unknown approval {approval_id!r}")
        return approval
