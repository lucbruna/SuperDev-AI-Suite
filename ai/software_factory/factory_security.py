"""Factory Security - Security validation for factory operations."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SecurityCheck(Enum):
    CODE_INJECTION = "code_injection"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    DEPENDENCY_VULNERABILITY = "dependency_vulnerability"
    SECRETS_EXPOSURE = "secrets_exposure"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"


class SecuritySeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityIssue:
    issue_id: str
    check: SecurityCheck
    severity: SecuritySeverity = SecuritySeverity.LOW
    description: str = ""
    file_path: str = ""
    line_number: int = 0
    recommendation: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False


class FactorySecurity:
    def __init__(self):
        self.issues: list[SecurityIssue] = []
        self.scan_results: dict[str, list[SecurityIssue]] = {}
        self.policies: dict[str, dict[str, Any]] = {}

    def create_policy(self, name: str, rules: dict[str, Any] = None) -> None:
        self.policies[name] = rules or {}

    def report_issue(
        self, check: SecurityCheck, severity: SecuritySeverity, description: str = "", file_path: str = "", **kwargs
    ) -> SecurityIssue:
        issue_id = hashlib.sha256(f"{check.value}{description}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        issue = SecurityIssue(
            issue_id=issue_id, check=check, severity=severity, description=description, file_path=file_path, **kwargs
        )
        self.issues.append(issue)
        return issue

    def resolve_issue(self, issue_id: str) -> bool:
        for issue in self.issues:
            if issue.issue_id == issue_id:
                issue.resolved = True
                return True
        return False

    def get_issues(self, severity: SecuritySeverity = None, resolved: bool = None) -> list[SecurityIssue]:
        issues = self.issues
        if severity:
            issues = [i for i in issues if i.severity == severity]
        if resolved is not None:
            issues = [i for i in issues if i.resolved == resolved]
        return issues

    def scan_project(self, project_id: str, files: list[str] = None) -> list[SecurityIssue]:
        found = []
        for f in files or []:
            issue = self.report_issue(SecurityCheck.CODE_INJECTION, SecuritySeverity.INFO, f"Scanned {f}", file_path=f)
            self.scan_results.setdefault(project_id, []).append(issue)
            found.append(issue)
        return found

    def get_score(self, project_id: str) -> float:
        issues = self.scan_results.get(project_id, [])
        if not issues:
            return 100.0
        unresolved = [i for i in issues if not i.resolved]
        return max(0, 100 - len(unresolved) * 5)

    def count_issues(self) -> int:
        return len(self.issues)
