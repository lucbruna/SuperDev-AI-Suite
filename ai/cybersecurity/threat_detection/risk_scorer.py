"""
Risk Assessment and Scoring
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import math


class RiskCategory(Enum):
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AVAILABILITY = "availability"


@dataclass
class RiskFactor:
    factor_id: str
    name: str
    category: RiskCategory
    likelihood: float = 0.5
    impact: float = 0.5
    weight: float = 1.0


@dataclass
class RiskAssessment:
    assessment_id: str
    factors: List[RiskFactor] = field(default_factory=list)
    overall_score: float = 0.0
    risk_level: str = "medium"
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CVSSVector:
    attack_vector: str = "N"
    attack_complexity: str = "L"
    privileges_required: str = "N"
    user_interaction: str = "N"
    scope: str = "U"
    confidentiality: str = "N"
    integrity: str = "N"
    availability: str = "N"


class RiskScorer:
    def __init__(self):
        self.factors: Dict[str, RiskFactor] = {}
        self.assessments: List[RiskAssessment] = []

    def add_factor(self, name: str, category: RiskCategory, likelihood: float = 0.5, impact: float = 0.5, weight: float = 1.0) -> RiskFactor:
        factor_id = f"factor_{len(self.factors)}"
        factor = RiskFactor(factor_id=factor_id, name=name, category=category, likelihood=likelihood, impact=impact, weight=weight)
        self.factors[factor_id] = factor
        return factor

    def calculate_risk_score(self, factors: List[RiskFactor] = None) -> float:
        factors = factors or list(self.factors.values())
        if not factors:
            return 0.0
        scores = [(f.likelihood * f.impact * f.weight) for f in factors]
        total_weight = sum(f.weight for f in factors)
        return sum(scores) / max(total_weight, 0.01)

    def assess(self, assessment_id: str) -> RiskAssessment:
        factors = list(self.factors.values())
        score = self.calculate_risk_score(factors)
        risk_level = "critical" if score > 0.8 else "high" if score > 0.6 else "medium" if score > 0.4 else "low"
        recs = ["Implement additional controls", "Increase monitoring"] if score > 0.6 else ["Maintain current controls"]
        assessment = RiskAssessment(assessment_id=assessment_id, factors=factors, overall_score=score, risk_level=risk_level, recommendations=recs)
        self.assessments.append(assessment)
        return assessment

    def calculate_cvss(self, vector: CVSSVector) -> float:
        av_map = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
        ac_map = {"L": 0.77, "H": 0.44}
        pr_map = {"N": 0.85, "L": 0.62, "H": 0.27}
        cia_map = {"N": 0.0, "L": 0.22, "H": 0.56}
        exploitability = 8.22 * av_map.get(vector.attack_vector, 0.85) * ac_map.get(vector.attack_complexity, 0.77) * pr_map.get(vector.privileges_required, 0.85)
        impact = 7.52 * (cia_map.get(vector.confidentiality, 0) + cia_map.get(vector.integrity, 0) + cia_map.get(vector.availability, 0))
        if impact <= 0:
            return 0.0
        base = min(1.0, (impact + exploitability) / 10)
        return round(base * 10, 1)

    def get_assessments(self) -> List[RiskAssessment]:
        return self.assessments

    def get_high_risk_factors(self, threshold: float = 0.6) -> List[RiskFactor]:
        return [f for f in self.factors.values() if f.likelihood * f.impact > threshold]

    def count(self) -> int:
        return len(self.factors)
