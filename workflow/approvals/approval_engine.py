from __future__ import annotations

import logging
from typing import Any

from .approval_models import Approval, ApprovalStatus
from .approval_workflow import ApprovalWorkflow
from .approval_notifier import ApprovalNotifier
from .approval_audit import ApprovalAudit


class ApprovalEngine:
    """Central engine for approval lifecycle."""

    def __init__(self) -> None:
        self._workflow = ApprovalWorkflow()
        self._notifier = ApprovalNotifier()
        self._audit = ApprovalAudit()
        self._log = logging.getLogger("superdev.workflow.approvals")

    def submit(self, approval: Approval) -> Approval:
        self._audit.log("submitted", approval.id)
        self._notifier.notify(approval)
        return approval

    def approve(self, approval_id: str) -> None:
        self._workflow.transition(approval_id, ApprovalStatus.APPROVED)
        self._audit.log("approved", approval_id)

    def reject(self, approval_id: str) -> None:
        self._workflow.transition(approval_id, ApprovalStatus.REJECTED)
        self._audit.log("rejected", approval_id)
