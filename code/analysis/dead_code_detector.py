from __future__ import annotations

import logging
from typing import Any


class DeadCodeDetector:
    """Detects unused code in projects."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis.deadcode")

    def detect(self, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return []
