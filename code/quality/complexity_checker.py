from __future__ import annotations

import logging
from typing import Any


class ComplexityChecker:
    """Checks code complexity metrics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.quality.complexity")

    def cyclomatic(self, code: str) -> int:
        self._log.debug("Calculating cyclomatic complexity")
        count = code.count("if ") + code.count("elif ") + code.count("for ") + code.count("while ")
        count += code.count("and ") + code.count("or ")
        return count

    def cognitive(self, code: str) -> int:
        self._log.debug("Calculating cognitive complexity")
        return code.count("if ") + code.count("for ") + code.count("while ") + code.count("except ")
