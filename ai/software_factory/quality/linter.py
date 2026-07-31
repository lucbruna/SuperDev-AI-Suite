"""Linter for detecting code quality issues."""
from typing import List
import re
from .models import QualityIssue, IssueSeverity, IssueCategory


class Linter:
    """Lints code for quality issues."""

    def __init__(self):
        self._patterns = [
            (r"print\(", IssueSeverity.INFO, IssueCategory.BEST_PRACTICE, "Consider using logging instead of print"),
            (r"except:\s*$", IssueSeverity.WARNING, IssueCategory.BEST_PRACTICE, "Bare except clause"),
            (r"TODO", IssueSeverity.INFO, IssueCategory.DOCUMENTATION, "TODO comment found"),
            (r"FIXME", IssueSeverity.WARNING, IssueCategory.DOCUMENTATION, "FIXME comment found"),
            (r"eval\(", IssueSeverity.ERROR, IssueCategory.SECURITY, "Use of eval() is dangerous"),
            (r"exec\(", IssueSeverity.ERROR, IssueCategory.SECURITY, "Use of exec() is dangerous"),
        ]

    def lint(self, content: str) -> List[QualityIssue]:
        issues = []
        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern, severity, category, message in self._patterns:
                if re.search(pattern, line):
                    issues.append(QualityIssue(
                        line_number=line_num,
                        severity=severity,
                        category=category,
                        message=message,
                    ))
        return issues

    def lint_line(self, line: str, line_number: int) -> List[QualityIssue]:
        issues = []
        for pattern, severity, category, message in self._patterns:
            if re.search(pattern, line):
                issues.append(QualityIssue(
                    line_number=line_number,
                    severity=severity,
                    category=category,
                    message=message,
                ))
        return issues
