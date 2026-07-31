from __future__ import annotations

import logging
from typing import Any


class RollbackPoint:
    """Captures a snapshot of state for later rollback."""

    def __init__(self, target: str, version: str) -> None:
        self._log = logging.getLogger("superdev.devops.rollback.point")
        self.target = target
        self.version = version
        self._snapshot: dict[str, Any] = {}

    def capture(self, state: dict[str, Any]) -> "RollbackPoint":
        raise NotImplementedError

    def restore(self) -> dict[str, Any]:
        raise NotImplementedError

    def diff(self, other: "RollbackPoint") -> dict[str, Any]:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError
