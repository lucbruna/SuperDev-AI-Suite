from __future__ import annotations

import logging


class ComplexityAnalysis:
    """Measures code complexity metrics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis.complexity")

    def measure(self, code: str) -> dict[str, int]:
        return {"lines": len(code.splitlines()), "cyclomatic": 1}
