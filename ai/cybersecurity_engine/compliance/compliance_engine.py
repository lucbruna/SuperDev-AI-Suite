"""Compliance engine."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ComplianceFramework(Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_ASSESSED = "not_assessed"


@dataclass
class ComplianceControl:
    control_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    framework: ComplianceFramework = ComplianceFramework.NIST
    title: str = ""
    description: str = ""
    status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED
    evidence: list[str] = field(default_factory=list)
    last_assessed: datetime | None = None
    next_review: datetime | None = None
    owner: str = ""


@dataclass
class ComplianceAssessment:
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    framework: ComplianceFramework = ComplianceFramework.NIST
    total_controls: int = 0
    compliant: int = 0
    non_compliant: int = 0
    partial: int = 0
    score: float = 0.0
    assessed_at: datetime = field(default_factory=datetime.now)


class ComplianceEngine:
    def __init__(self):
        self._controls: dict[str, ComplianceControl] = {}
        self._assessments: list[ComplianceAssessment] = []
        self._frameworks: dict[ComplianceFramework, list[str]] = {}

    def add_control(self, control: ComplianceControl) -> None:
        self._controls[control.control_id] = control
        if control.framework not in self._frameworks:
            self._frameworks[control.framework] = []
        self._frameworks[control.framework].append(control.control_id)

    def get_control(self, control_id: str) -> ComplianceControl | None:
        return self._controls.get(control_id)

    def update_control_status(
        self, control_id: str, status: ComplianceStatus, evidence: list[str] | None = None
    ) -> bool:
        control = self._controls.get(control_id)
        if not control:
            return False
        control.status = status
        control.last_assessed = datetime.now()
        if evidence:
            control.evidence.extend(evidence)
        return True

    def assess_framework(self, framework: ComplianceFramework) -> ComplianceAssessment:
        control_ids = self._frameworks.get(framework, [])
        controls = [self._controls[cid] for cid in control_ids if cid in self._controls]
        total = len(controls)
        compliant = sum(1 for c in controls if c.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for c in controls if c.status == ComplianceStatus.NON_COMPLIANT)
        partial = sum(1 for c in controls if c.status == ComplianceStatus.PARTIAL)
        score = (compliant / total * 100) if total > 0 else 0.0
        assessment = ComplianceAssessment(
            framework=framework,
            total_controls=total,
            compliant=compliant,
            non_compliant=non_compliant,
            partial=partial,
            score=score,
        )
        self._assessments.append(assessment)
        return assessment

    def get_framework_controls(self, framework: ComplianceFramework) -> list[ComplianceControl]:
        control_ids = self._frameworks.get(framework, [])
        return [self._controls[cid] for cid in control_ids if cid in self._controls]

    def get_assessments(self, framework: ComplianceFramework | None = None) -> list[ComplianceAssessment]:
        assessments = list(self._assessments)
        if framework:
            assessments = [a for a in assessments if a.framework == framework]
        return assessments

    def get_gaps(self, framework: ComplianceFramework) -> list[ComplianceControl]:
        return [
            c
            for c in self._controls.values()
            if c.framework == framework and c.status in (ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIAL)
        ]

    def get_stats(self) -> dict:
        controls = list(self._controls.values())
        return {
            "total_controls": len(controls),
            "compliant": len([c for c in controls if c.status == ComplianceStatus.COMPLIANT]),
            "non_compliant": len([c for c in controls if c.status == ComplianceStatus.NON_COMPLIANT]),
            "partial": len([c for c in controls if c.status == ComplianceStatus.PARTIAL]),
            "not_assessed": len([c for c in controls if c.status == ComplianceStatus.NOT_ASSESSED]),
            "frameworks": len(self._frameworks),
            "assessments": len(self._assessments),
        }
