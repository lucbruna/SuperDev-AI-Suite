"""Quality models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class QualityCheckType(Enum):
    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"


class QualityStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class QualityRule:
    rule_id: str
    name: str = ""
    check_type: QualityCheckType = QualityCheckType.COMPLETENESS
    config: Dict[str, Any] = field(default_factory=dict)
    threshold: float = 0.95
    enabled: bool = True


@dataclass
class QualityCheck:
    check_id: str
    dataset: str = ""
    rule_id: str = ""
    status: QualityStatus = QualityStatus.PASSED
    score: float = 1.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class QualityReport:
    report_id: str
    dataset: str = ""
    checks: List[QualityCheck] = field(default_factory=list)
    overall_score: float = 1.0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    generated_at: datetime = field(default_factory=datetime.now)
