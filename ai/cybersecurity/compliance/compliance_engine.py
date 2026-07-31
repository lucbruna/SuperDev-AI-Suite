"""
Compliance Framework Engine
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class Framework(Enum):
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist"


class ControlStatus(Enum):
    IMPLEMENTED = "implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class Control:
    control_id: str
    framework: Framework
    name: str
    description: str = ""
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    evidence: str = ""
    owner: str = ""
    last_assessed: Optional[datetime] = None


@dataclass
class ComplianceAssessment:
    assessment_id: str
    framework: Framework
    controls: List[Control] = field(default_factory=list)
    score: float = 0.0
    assessed_at: datetime = field(default_factory=datetime.now)
    assessor: str = ""


@dataclass
class GapAnalysis:
    framework: Framework
    total_controls: int = 0
    implemented: int = 0
    partial: int = 0
    not_implemented: int = 0
    gaps: List[Control] = field(default_factory=list)


class ComplianceEngine:
    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self.assessments: List[ComplianceAssessment] = []
        self.gap_analyses: List[GapAnalysis] = []

    def add_control(self, control_id: str, framework: Framework, name: str, description: str = "") -> Control:
        control = Control(control_id=control_id, framework=framework, name=name, description=description)
        self.controls[control_id] = control
        return control

    def update_control_status(self, control_id: str, status: ControlStatus, evidence: str = "") -> bool:
        control = self.controls.get(control_id)
        if control:
            control.status = status
            control.evidence = evidence
            control.last_assessed = datetime.now()
            return True
        return False

    def assess(self, framework: Framework, assessor: str = "") -> ComplianceAssessment:
        framework_controls = [c for c in self.controls.values() if c.framework == framework]
        implemented = sum(1 for c in framework_controls if c.status == ControlStatus.IMPLEMENTED)
        score = (implemented / max(len(framework_controls), 1)) * 100
        assessment = ComplianceAssessment(assessment_id=hashlib.sha256(f"{framework.value}{datetime.now().isoformat()}".encode()).hexdigest()[:16], framework=framework, controls=framework_controls, score=score, assessor=assessor)
        self.assessments.append(assessment)
        return assessment

    def gap_analysis(self, framework: Framework) -> GapAnalysis:
        framework_controls = [c for c in self.controls.values() if c.framework == framework]
        implemented = sum(1 for c in framework_controls if c.status == ControlStatus.IMPLEMENTED)
        partial = sum(1 for c in framework_controls if c.status == ControlStatus.PARTIALLY_IMPLEMENTED)
        not_impl = sum(1 for c in framework_controls if c.status == ControlStatus.NOT_IMPLEMENTED)
        gaps = [c for c in framework_controls if c.status in (ControlStatus.NOT_IMPLEMENTED, ControlStatus.PARTIALLY_IMPLEMENTED)]
        analysis = GapAnalysis(framework=framework, total_controls=len(framework_controls), implemented=implemented, partial=partial, not_implemented=not_impl, gaps=gaps)
        self.gap_analyses.append(analysis)
        return analysis

    def get_controls_by_framework(self, framework: Framework) -> List[Control]:
        return [c for c in self.controls.values() if c.framework == framework]

    def get_controls_by_status(self, status: ControlStatus) -> List[Control]:
        return [c for c in self.controls.values() if c.status == status]

    def get_control(self, control_id: str) -> Optional[Control]:
        return self.controls.get(control_id)

    def count(self) -> int:
        return len(self.controls)
