from __future__ import annotations

from typing import Any

from .approval_models import Approval


class ApprovalPolicy:
    """Defines approval policy rules."""

    def __init__(self, required_reviewers: int = 1) -> None:
        self._required_reviewers = required_reviewers

    def is_satisfied(self, approval: Approval) -> bool:
        return len(set(approval.reviewers)) >= self._required_reviewers
