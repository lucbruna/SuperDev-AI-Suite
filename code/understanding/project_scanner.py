from __future__ import annotations

import logging


class ProjectScanner:
    """Scans project structure for understanding."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.understanding.scanner")

    def scan(self, path: str) -> list[dict]:
        return []
