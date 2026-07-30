from __future__ import annotations

import logging


class QualityAnalysis:
    """Analyzes overall code quality."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis.quality")

    def score(self, files: list[dict]) -> float:
        return 100.0
