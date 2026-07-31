from __future__ import annotations

import logging
from typing import Any


class ApprovalStage:
    """CI/CD approval stage — manual or automatic gating."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.approval")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def approve(self, stage_id: str, user: str) -> bool:
        raise NotImplementedError

    def reject(self, stage_id: str, user: str, reason: str) -> bool:
        raise NotImplementedError
