from __future__ import annotations

import logging
from ..code_models import CodeFile, CodeIssue


class SecurityAnalysis:
    """Analyzes code for security vulnerabilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis.security")

    def analyze(self, files: list[CodeFile]) -> list[CodeIssue]:
        return []
