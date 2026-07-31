"""Approval lifecycle management."""

from __future__ import annotations

import time
from typing import Any

from collaboration.collaboration_models import (ApprovalRecord,
                                                ApprovalStatus, EntityKind)
from collaboration.collaboration_protocols import new_id
from collaboration.approvals.approval_flow import ApprovalFlow
from collaboration.approvals.approval_history import ApprovalHistory


class ApprovalManager:
    """CRUD for approvals with multi-step flows."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
        self.flow = ApprovalFlow()
        self._history: dict[str, ApprovalHistory] = {}

    def start(self, target_kind: EntityKind, target_id: str,
              requested_by: str,
              flow: str = "manager") -> ApprovalRecord:
        approval = ApprovalRecord(
            approval_id=new_id("appr"), target_kind=target_kind,
            target_id=target_id, flow=flow, requested_by=requested_by,
            steps=self.flow.steps_for(flow), status=ApprovalStatus.PENDING)
        if self.registry is not None:
            self.registry.register_approval(approval.approval_id, approval)
        self._history[approval.approval_id] = ApprovalHistory()
        return approval

    def get(self, approval_id: str) -> ApprovalRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_approval(approval_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_approvals()

    def remove(self, approval_id: str) -> bool:
        self._history.pop(approval_id, None)
        if self.registry is not None:
            return self.registry.remove_approval(approval_id)
        return False

    def history(self, approval_id: str) -> ApprovalHistory:
        history = self._history.get(approval_id)
        if history is None:
            history = ApprovalHistory()
            self._history[approval_id] = history
        return history

    def decide(self, approval_id: str, approved: bool, decider: str,
               reason: str = "") -> ApprovalRecord | None:
        approval = self.get(approval_id)
        if approval is None:
            return None
        history = self.history(approval_id)
        step = approval.steps[approval.current_step] \
            if approval.current_step < len(approval.steps) \
            else {"step": approval.current_step + 1, "label": "final"}
        history.record(step.get("step", 0), step.get("label", ""),
                       decider, approved, reason)
        if not approved:
            approval.status = ApprovalStatus.REJECTED
            approval.decided_by = decider
            approval.decided_at = time.time()
            approval.reason = reason
            return approval
        approval.current_step += 1
        if approval.current_step >= len(approval.steps):
            approval.status = ApprovalStatus.APPROVED
            approval.decided_by = decider
            approval.decided_at = time.time()
            approval.reason = reason
        return approval

    def cancel(self, approval_id: str, decider: str) -> ApprovalRecord | None:
        approval = self.get(approval_id)
        if approval is None:
            return None
        approval.status = ApprovalStatus.CANCELLED
        approval.decided_by = decider
        approval.decided_at = time.time()
        approval.reason = "cancelled"
        return approval

    def by_target(self, target_id: str) -> list[ApprovalRecord]:
        if self.registry is None:
            return []
        approvals = []
        for approval_id in self.registry.list_approvals():
            approval = self.registry.get_approval(approval_id)
            if approval is not None and approval.target_id == target_id:
                approvals.append(approval)
        return approvals

    def count(self) -> int:
        if self.registry is None:
            return 0
        return len(self.registry.list_approvals())
