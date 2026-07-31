from __future__ import annotations

import logging
from typing import Any


class ConflictResolver:
    """Resolves conflicts during migration."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.migration.conflict")

    def detect(self, source: str, target: str) -> list[dict[str, Any]]:
        self._log.debug("Detecting conflicts between source and target")
        return []

    def resolve(self, conflict: dict[str, Any], strategy: str = "ours") -> str | None:
        self._log.info("Resolving conflict with strategy %s", strategy)
        return None
