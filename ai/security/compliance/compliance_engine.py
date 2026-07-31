"""Compliance engine."""

from __future__ import annotations

from enum import Enum
from typing import Any


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
        self.last_assessed: float | None = None


class ComplianceEngine:
    def __init__(self) -> None:
        self._controls: dict[str, ComplianceControl] = {}
        self._assessments: dict[str, list[dict[str, Any]]] = {}

    def register_control(
        self, control_id: str, name: str, description: str, standard: ComplianceStandard
    ) -> ComplianceControl:
        ctrl = ComplianceControl(control_id, name, description, standard)
        self._controls[control_id] = ctrl
        return ctrl

    def assess(self, control_id: str, status: str, notes: str = "") -> bool:
        ctrl = self._controls.get(control_id)
        if ctrl:
            ctrl.status = status
            import time

            ctrl.last_assessed = time.time()
            self._assessments.setdefault(control_id, []).append(
                {"status": status, "notes": notes, "timestamp": ctrl.last_assessed}
            )
            return True
        return False

    def get_status(self, control_id: str) -> str | None:
        ctrl = self._controls.get(control_id)
        return ctrl.status if ctrl else None

    def get_controls_by_standard(self, standard: ComplianceStandard) -> list[dict[str, Any]]:
        return [
            {"id": c.control_id, "name": c.name, "status": c.status}
            for c in self._controls.values()
            if c.standard == standard
        ]

    def compliance_score(self, standard: ComplianceStandard) -> dict[str, Any]:
        controls = [c for c in self._controls.values() if c.standard == standard]
        total = len(controls)
        compliant = sum(1 for c in controls if c.status == "compliant")
        return {"total": total, "compliant": compliant, "score": (compliant / max(total, 1)) * 100}

    def list_controls(self) -> list[str]:
        return list(self._controls.keys())
