"""Compliance engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum

class ComplianceStandard(Enum):
    GDPR = "gdpr"
    LGPD = "lgpd"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"

class ComplianceControl:
    def __init__(self, control_id: str, name: str, description: str, standard: ComplianceStandard) -> None:
        self.control_id = control_id
        self.name = name
        self.description = description
        self.standard = standard
        self.status = "not_assessed"
        self.last_assessed: Optional[float] = None

class ComplianceEngine:
    def __init__(self) -> None:
        self._controls: Dict[str, ComplianceControl] = {}
        self._assessments: Dict[str, List[Dict[str, Any]]] = {}
    def register_control(self, control_id: str, name: str, description: str, standard: ComplianceStandard) -> ComplianceControl:
        ctrl = ComplianceControl(control_id, name, description, standard)
        self._controls[control_id] = ctrl
        return ctrl
    def assess(self, control_id: str, status: str, notes: str = "") -> bool:
        ctrl = self._controls.get(control_id)
        if ctrl:
            ctrl.status = status
            import time
            ctrl.last_assessed = time.time()
            self._assessments.setdefault(control_id, []).append({"status": status, "notes": notes, "timestamp": ctrl.last_assessed})
            return True
        return False
    def get_status(self, control_id: str) -> Optional[str]:
        ctrl = self._controls.get(control_id)
        return ctrl.status if ctrl else None
    def get_controls_by_standard(self, standard: ComplianceStandard) -> List[Dict[str, Any]]:
        return [{"id": c.control_id, "name": c.name, "status": c.status} for c in self._controls.values() if c.standard == standard]
    def compliance_score(self, standard: ComplianceStandard) -> Dict[str, Any]:
        controls = [c for c in self._controls.values() if c.standard == standard]
        total = len(controls)
        compliant = sum(1 for c in controls if c.status == "compliant")
        return {"total": total, "compliant": compliant, "score": (compliant / max(total, 1)) * 100}
    def list_controls(self) -> List[str]:
        return list(self._controls.keys())
