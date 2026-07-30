from __future__ import annotations

import logging
from typing import Any

from ..code_models import CodeFile, CodeIssue, CodeModule


class CodeAnalyzer:
    """Central analyzer for code quality and structure."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.analysis")

    def analyze(self, files: list[CodeFile]) -> list[CodeIssue]:
        issues: list[CodeIssue] = []
        for f in files:
            if not f.content:
                issues.append(CodeIssue(file=f.path, message="Empty file"))
        self._log.info("Analyzed %d files, found %d issues", len(files), len(issues))
        return issues
