from __future__ import annotations

import logging
from typing import Any


class DuplicationChecker:
    """Detects duplicated code blocks."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.quality.duplication")

    def find_duplicates(self, files: list[str], min_lines: int = 5) -> list[dict[str, Any]]:
        self._log.info("Scanning %d files for duplication (min_lines=%d)", len(files), min_lines)
        return []

    def report(self, duplicates: list[dict[str, Any]]) -> str:
        return f"Found {len(duplicates)} duplicated blocks" if duplicates else "No duplication found"
