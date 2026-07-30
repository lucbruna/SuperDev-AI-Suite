from __future__ import annotations

import logging


class CodeSecurity:
    """Security checks for code operations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.security")

    def can_read(self, path: str) -> bool:
        return True

    def can_write(self, path: str) -> bool:
        return True

    def can_execute(self, path: str) -> bool:
        return False
