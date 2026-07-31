"""Data models for code quality."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class IssueSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IssueCategory(Enum):
    STYLE = "style"
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    BEST_PRACTICE = "best_practice"


@dataclass
class QualityIssue:
    """A code quality issue."""
    issue_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    file_path: str = ""
    line_number: int = 0
    column: int = 0
    severity: IssueSeverity = IssueSeverity.WARNING
    category: IssueCategory = IssueCategory.STYLE
    message: str = ""
    rule_id: str = ""
    suggestion: str = ""


@dataclass
class QualityRule:
    """A quality rule definition."""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    category: IssueCategory = IssueCategory.STYLE
    severity: IssueSeverity = IssueSeverity.WARNING
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "category": self.category.value,
            "severity": self.severity.value,
        }


@dataclass
class QualityMetric:
    """A quality metric measurement."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    value: float = 0.0
    threshold: float = 0.0
    unit: str = ""
    measured_at: datetime = field(default_factory=datetime.utcnow)

    def is_passing(self) -> bool:
        return self.value >= self.threshold


@dataclass
class QualityReport:
    """A comprehensive quality analysis report."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    file_path: str = ""
    issues: List[QualityIssue] = field(default_factory=list)
    metrics: List[QualityMetric] = field(default_factory=list)
    score: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.WARNING)
