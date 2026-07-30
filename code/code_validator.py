from __future__ import annotations

import logging

from .code_models import CodeFile, CodeIssue, CodeIssueSeverity


class CodeValidator:
    """Validates code files for common issues."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.validator")

    def validate(self, file: CodeFile) -> list[CodeIssue]:
        issues: list[CodeIssue] = []
        if not file.content:
            issues.append(CodeIssue(file=file.path, message="Empty file", severity=CodeIssueSeverity.INFO))
        return issues
