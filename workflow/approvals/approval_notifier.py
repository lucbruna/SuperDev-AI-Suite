from __future__ import annotations

import logging
from typing import Any

from .approval_models import Approval


class ApprovalNotifier:
    """Sends notifications for approval events."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.approvals.notifier")

    def notify(self, approval: Approval, message: str | None = None) -> None:
        msg = message or f"Approval {approval.id} requires review"
        self._log.info("Notification: %s", msg)
