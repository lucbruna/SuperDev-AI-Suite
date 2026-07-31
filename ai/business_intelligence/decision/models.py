"""Decision engine models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DecisionType(Enum):
    RULE_BASED = "rule_based"
    ML_BASED = "ml_based"
    HYBRID = "hybrid"
    MANUAL = "manual"


class DecisionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Rule:
    rule_id: str
    name: str
    condition: str = ""
    action: str = ""
    priority: int = 0
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionRequest:
    request_id: str
    decision_type: DecisionType = DecisionType.RULE_BASED
    context: dict[str, Any] = field(default_factory=dict)
    rules: list[Rule] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    timeout_seconds: float = 30.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionResult:
    request_id: str
    status: DecisionStatus = DecisionStatus.PENDING
    decision: str | None = None
    confidence: float = 0.0
    reasoning: list[str] = field(default_factory=list)
    applied_rules: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    executed_at: datetime | None = None
    error: str | None = None


@dataclass
class DecisionPolicy:
    policy_id: str
    name: str
    description: str = ""
    rules: list[Rule] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    auto_execute: bool = False
    require_approval: bool = True
    timeout_seconds: float = 60.0
