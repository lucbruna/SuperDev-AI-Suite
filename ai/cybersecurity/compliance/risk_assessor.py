"""
Risk Assessment Engine
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class TreatmentType(Enum):
    MITIGATE = "mitigate"
    TRANSFER = "transfer"
    ACCEPT = "accept"
    AVOID = "avoid"


@dataclass
class Risk:
    risk_id: str
    name: str
    description: str = ""
    likelihood: float = 0.5
    impact: float = 0.5
    risk_level: RiskLevel = RiskLevel.MEDIUM
    score: float = 0.0
    treatment: TreatmentType = TreatmentType.MITIGATE
    owner: str = ""
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.now)
    mitigations: list[str] = field(default_factory=list)


@dataclass
class RiskRegister:
    register_id: str
    risks: list[Risk] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class RiskAssessor:
    def __init__(self):
        self.risks: dict[str, Risk] = {}
        self.registers: list[RiskRegister] = []

    def identify_risk(self, name: str, likelihood: float = 0.5, impact: float = 0.5, **kwargs) -> Risk:
        risk_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        score = likelihood * impact
        if score >= 0.8:
            level = RiskLevel.CRITICAL
        elif score >= 0.6:
            level = RiskLevel.HIGH
        elif score >= 0.4:
            level = RiskLevel.MEDIUM
        elif score >= 0.2:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.NEGLIGIBLE
        risk = Risk(
            risk_id=risk_id, name=name, likelihood=likelihood, impact=impact, risk_level=level, score=score, **kwargs
        )
        self.risks[risk_id] = risk
        return risk

    def update_risk(self, risk_id: str, **kwargs) -> bool:
        risk = self.risks.get(risk_id)
        if risk:
            for k, v in kwargs.items():
                if hasattr(risk, k):
                    setattr(risk, k, v)
            return True
        return False

    def add_mitigation(self, risk_id: str, mitigation: str) -> bool:
        risk = self.risks.get(risk_id)
        if risk:
            risk.mitigations.append(mitigation)
            return True
        return False

    def get_by_level(self, level: RiskLevel) -> list[Risk]:
        return [r for r in self.risks.values() if r.risk_level == level]

    def get_open_risks(self) -> list[Risk]:
        return [r for r in self.risks.values() if r.status == "open"]

    def get_risk(self, risk_id: str) -> Risk | None:
        return self.risks.get(risk_id)

    def create_register(self) -> RiskRegister:
        register = RiskRegister(register_id=f"reg_{len(self.registers)}", risks=list(self.risks.values()))
        self.registers.append(register)
        return register

    def count(self) -> int:
        return len(self.risks)
