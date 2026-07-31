from __future__ import annotations

import logging
from typing import Any


class EnvironmentPromotion:
    """Promotes deployments and configs between environments."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.environments.promotion")
        self._history: list[dict[str, Any]] = []

    def promote(self, source: str, target: str, artifacts: list[str]) -> dict[str, Any]:
        raise NotImplementedError

    def approve(self, promotion_id: str, approver: str) -> bool:
        raise NotImplementedError

    def reject(self, promotion_id: str, reason: str) -> bool:
        raise NotImplementedError

    def history(self, environment: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def status(self, promotion_id: str) -> dict[str, Any]:
        raise NotImplementedError
