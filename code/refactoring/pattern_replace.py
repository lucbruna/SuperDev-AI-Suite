from __future__ import annotations

import logging
from typing import Any


class PatternReplace:
    """Replaces code patterns with new implementations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.refactoring.pattern")

    def replace(self, code: str, pattern: str, replacement: str) -> str:
        self._log.info("Replacing pattern: %s", pattern)
        return code.replace(pattern, replacement)
