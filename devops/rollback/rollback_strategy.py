from __future__ import annotations

import logging
from typing import Any


class RollbackStrategy:
    """Selects and configures rollback strategies."""

    def __init__(self, strategy: str = "versioned") -> None:
        self._log = logging.getLogger("superdev.devops.rollback.strategy")
        self.strategy = strategy

    def available(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def plan(self, target: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def estimate(self, target: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError
