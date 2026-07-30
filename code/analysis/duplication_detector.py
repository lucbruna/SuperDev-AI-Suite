from __future__ import annotations

import logging
from typing import Any


class DuplicationDetector:
    """Detects duplicated code blocks."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis.duplication")

    def detect(self, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return []
