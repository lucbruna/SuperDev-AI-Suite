"""
Legal Models - Core legal and compliance data models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ContractStatus(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    AMENDED = "amended"


class ContractType(Enum):
    COMMERCIAL = "commercial"
    SUPPLIER = "supplier"
    CLIENT = "client"
    EMPLOYEE = "employee"
    PARTNER = "partner"
    NDA = "nda"
    LEASE = "lease"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"


class DocumentType(Enum):
    CONTRACT = "contract"
    OPINION = "opinion"
    LICENSE = "license"
    CERTIFICATE = "certificate"
    POLICY = "policy"
    REPORT = "report"
    EVIDENCE = "evidence"


class CaseStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    APPEALED = "appealed"


@dataclass
class Clause:
    id: str
    text: str
    type: str = ""
    category: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    recommendation: str = ""
    is_standard: bool = False


@dataclass
class Party:
    id: str
    name: str
    legal_name: str = ""
    tax_id: str = ""
    address: str = ""
    contact_email: str = ""
    role: str = ""


@dataclass
class Contract:
    id: str
    title: str
    contract_type: ContractType = ContractType.COMMERCIAL
    status: ContractStatus = ContractStatus.DRAFT
    parties: List[Party] = field(default_factory=list)
    clauses: List[Clause] = field(default_factory=list)
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    auto_renewal: bool = False
    value: float = 0.0
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    jurisdiction: str = ""
    governing_law: str = ""
    reviewed_by: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Obligation:
    id: str
    contract_id: str
    description: str
    party: str
    due_date: Optional[datetime] = None
    status: str = "pending"
    completed_at: Optional[datetime] = None


@dataclass
class LegalDocument:
    id: str
    title: str
    document_type: DocumentType = DocumentType.CONTRACT
    category: str = ""
    tags: List[str] = field(default_factory=list)
    content: str = ""
    summary: str = ""
    version: str = "1.0"
    author: str = ""
    department: str = ""
    confidential: bool = False
    retention_years: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = None


@dataclass
class Regulation:
    id: str
    name: str
    authority: str = ""
    jurisdiction: str = ""
    description: str = ""
    impact_areas: List[str] = field(default_factory=list)
    effective_date: Optional[datetime] = None
    version: str = "1.0"
    status: str = "active"
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceControl:
    id: str
    name: str
    regulation_id: str = ""
    description: str = ""
    status: str = "active"
    passing: bool = True
    last_checked: Optional[datetime] = None
    owner: str = ""


@dataclass
class ComplianceReport:
    period: str
    overall_score: float = 0.0
    status: ComplianceStatus = ComplianceStatus.COMPLIANT
    violations_count: int = 0
    controls_total: int = 0
    controls_passing: int = 0
    violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskAssessment:
    overall_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    contractual_risk: float = 0.0
    regulatory_risk: float = 0.0
    operational_risk: float = 0.0
    financial_exposure: float = 0.0
    factors: List[str] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MitigationPlan:
    id: str
    risk_id: str
    description: str
    actions: List[Dict[str, Any]] = field(default_factory=list)
    owner: str = ""
    deadline: Optional[datetime] = None
    status: str = "open"
    effectiveness: float = 0.0


@dataclass
class AuditFinding:
    id: str
    audit_id: str
    title: str
    description: str = ""
    severity: str = "medium"
    status: str = "open"
    remediated_at: Optional[datetime] = None


@dataclass
class AuditReport:
    report_id: str
    period: str
    scope: str = ""
    status: str = "completed"
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    findings_resolved: int = 0
    findings: List[AuditFinding] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvidenceRecord:
    id: str
    audit_id: str
    description: str
    document_id: str = ""
    collected_by: str = ""
    collected_at: datetime = field(default_factory=datetime.utcnow)
    hash: str = ""


@dataclass
class PolicyDocument:
    id: str
    title: str
    category: str = ""
    content: str = ""
    version: str = "1.0"
    status: str = "active"
    effective_date: Optional[datetime] = None
    owner: str = ""
    department: str = ""
    requires_acknowledgment: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyAcknowledgment:
    id: str
    policy_id: str
    employee_id: str
    acknowledged_at: datetime = field(default_factory=datetime.utcnow)
    ip_address: str = ""
    status: str = "acknowledged"


@dataclass
class LitigationCase:
    id: str
    title: str
    case_number: str = ""
    court: str = ""
    jurisdiction: str = ""
    parties: List[str] = field(default_factory=list)
    status: CaseStatus = CaseStatus.OPEN
    filed_date: Optional[datetime] = None
    next_deadline: Optional[datetime] = None
    estimated_value: float = 0.0
    probability_win: float = 0.0
    assigned_to: str = ""
    description: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Deadline:
    id: str
    case_id: str
    title: str
    due_date: datetime
    description: str = ""
    status: str = "pending"
    reminder_sent: bool = False


@dataclass
class LegalPrediction:
    case_id: str
    predicted_outcome: str = ""
    confidence_score: float = 0.0
    estimated_duration_months: int = 0
    estimated_cost: float = 0.0
    factors: List[str] = field(default_factory=list)
    recommended_strategy: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LegalAlert:
    id: str
    alert_type: str
    severity: str
    title: str
    message: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
