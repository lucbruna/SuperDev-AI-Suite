"""ERP Security — Security validation for ERP operations."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ERPSecurityCheck(Enum):
    DATA_ACCESS = "data_access"
    PERMISSION = "permission"
    ENCRYPTION = "encryption"
    AUDIT = "audit"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"


class ERPSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ERPSecurityIssue:
    issue_id: str
    check: ERPSecurityCheck
    severity: ERPSeverity = ERPSeverity.LOW
    description: str = ""
    resource: str = ""
    recommendation: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False


class ERPSecurity:
    def __init__(self):
        self.issues: list[ERPSecurityIssue] = []
        self.policies: dict[str, dict[str, Any]] = {}

    def create_policy(self, name: str, rules: dict[str, Any] | None = None) -> None:
        self.policies[name] = rules or {}

    def report_issue(self, check: ERPSecurityCheck, severity: ERPSeverity, description: str = "", resource: str = "", **kwargs) -> ERPSecurityIssue:
        issue_id = hashlib.sha256(f"{check.value}{description}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        issue = ERPSecurityIssue(issue_id=issue_id, check=check, severity=severity, description=description, resource=resource, **kwargs)
        self.issues.append(issue)
        return issue

    def resolve_issue(self, issue_id: str) -> bool:
        for issue in self.issues:
            if issue.issue_id == issue_id:
                issue.resolved = True
                return True
        return False

    def get_issues(self, severity: ERPSeverity | None = None, resolved: bool | None = None) -> list[ERPSecurityIssue]:
        issues = self.issues
        if severity:
            issues = [i for i in issues if i.severity == severity]
        if resolved is not None:
            issues = [i for i in issues if i.resolved == resolved]
        return issues

    def get_score(self) -> float:
        if not self.issues:
            return 100.0
        unresolved = [i for i in self.issues if not i.resolved]
        return max(0, 100 - len(unresolved) * 5)

    def count_issues(self) -> int:
        return len(self.issues)
