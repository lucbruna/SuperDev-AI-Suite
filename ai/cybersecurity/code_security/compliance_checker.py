"""
Compliance Framework Checker
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class Framework(Enum):
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    ISO27001 = "iso27001"


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class Control:
    control_id: str
    framework: Framework
    description: str
    status: ComplianceStatus = ComplianceStatus.NOT_APPLICABLE
    evidence: str = ""
    remediation: str = ""


@dataclass
class ComplianceReport:
    framework: Framework
    total_controls: int
    compliant: int
    non_compliant: int
    partial: int
    score: float = 0.0
    controls: List[Control] = field(default_factory=list)


class ComplianceChecker:
    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self.reports: List[ComplianceReport] = []

    def add_control(self, control: Control) -> None:
        self.controls[control.control_id] = control

    def evaluate_control(self, control_id: str, status: ComplianceStatus, evidence: str = "") -> bool:
        control = self.controls.get(control_id)
        if control:
            control.status = status
            control.evidence = evidence
            return True
        return False

    def generate_report(self, framework: Framework) -> ComplianceReport:
        framework_controls = [c for c in self.controls.values() if c.framework == framework]
        compliant = sum(1 for c in framework_controls if c.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for c in framework_controls if c.status == ComplianceStatus.NON_COMPLIANT)
        partial = sum(1 for c in framework_controls if c.status == ComplianceStatus.PARTIAL)
        total = len(framework_controls)
        score = (compliant / max(total, 1)) * 100
        report = ComplianceReport(framework=framework, total_controls=total, compliant=compliant, non_compliant=non_compliant, partial=partial, score=score, controls=framework_controls)
        self.reports.append(report)
        return report

    def get_non_compliant(self, framework: Framework = None) -> List[Control]:
        results = [c for c in self.controls.values() if c.status == ComplianceStatus.NON_COMPLIANT]
        if framework:
            results = [c for c in results if c.framework == framework]
        return results

    def get_by_framework(self, framework: Framework) -> List[Control]:
        return [c for c in self.controls.values() if c.framework == framework]

    def get_last_report(self, framework: Framework = None) -> Optional[ComplianceReport]:
        reports = self.reports
        if framework:
            reports = [r for r in reports if r.framework == framework]
        return reports[-1] if reports else None

    def count(self) -> int:
        return len(self.controls)
