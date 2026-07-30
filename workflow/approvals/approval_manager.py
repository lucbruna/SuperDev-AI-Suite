from __future__ import annotations

import logging
from typing import Any

from .approval_models import Approval, ApprovalStatus


class ApprovalManager:
    """Manages approval records and state transitions."""

    def __init__(self) -> None:
        self._approvals: dict[str, Approval] = {}
        self._log = logging.getLogger("superdev.workflow.approvals.manager")

    def create(self, approval: Approval) -> None:
        self._approvals[approval.id] = approval
        self._log.info("Created approval %s", approval.id)

    def get(self, approval_id: str) -> Approval | None:
        return self._approvals.get(approval_id)

    def update_status(self, approval_id: str, status: ApprovalStatus) -> None:
        appr = self._approvals.get(approval_id)
        if appr:
            appr.status = status
