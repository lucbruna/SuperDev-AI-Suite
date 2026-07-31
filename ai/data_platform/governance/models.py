"""Governance models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class AccessLevel(Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ComplianceStandard(Enum):
    LGPD = "lgpd"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"


class PolicyStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


@dataclass
class AccessPolicy:
    policy_id: str
    user_id: str = ""
    dataset: str = ""
    access_level: AccessLevel = AccessLevel.READ
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RetentionPolicy:
    policy_id: str
    dataset: str = ""
    retention_days: int = 365
    auto_delete: bool = False
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditEntry:
    entry_id: str
    user_id: str = ""
    dataset: str = ""
    action: str = ""
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceRule:
    rule_id: str
    standard: ComplianceStandard = ComplianceStandard.LGPD
    name: str = ""
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
