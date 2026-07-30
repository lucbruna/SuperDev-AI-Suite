from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile, CodeIssue


class StaticAnalysis:
    """Performs static code analysis."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis.static")

    def analyze(self, file: CodeFile) -> list[CodeIssue]:
        return []
