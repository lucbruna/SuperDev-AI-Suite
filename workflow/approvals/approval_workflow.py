from __future__ import annotations

import logging
from typing import Any

from .approval_models import Approval, ApprovalStatus


class ApprovalWorkflow:
    """Manages approval workflow state transitions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.approvals.workflow")

    def transition(self, approval_id: str, new_status: ApprovalStatus) -> None:
        self._log.info("Transition %s -> %s", approval_id, new_status.value)
