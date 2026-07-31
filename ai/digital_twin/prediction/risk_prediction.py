"""Risk prediction."""
from __future__ import annotations
from typing import Any, Dict, List

class RiskPredictor:
    def __init__(self) -> None:
        self._assessments: List[Dict[str, Any]] = []
    def assess(self, scenario: Dict[str, Any], risk_factors: List[str] = None) -> Dict[str, Any]:
        risk_factors = risk_factors or ["financial", "operational", "strategic", "market"]
        risks = {}
        for factor in risk_factors:
            risks[factor] = {"probability": 0.3, "impact": 0.5, "score": 0.15}
        overall = sum(r["score"] for r in risks.values()) / len(risks) if risks else 0
        assessment = {"scenario": scenario, "risks": risks, "overall_risk": overall, "level": "medium" if overall < 0.5 else "high"}
        self._assessments.append(assessment)
        return assessment
    def get_highest_risks(self, limit: int = 5) -> List[Dict[str, Any]]:
        all_risks = []
        for a in self._assessments:
            for factor, data in a.get("risks", {}).items():
                all_risks.append({"factor": factor, "score": data.get("score", 0), "assessment": a.get("scenario", {})})
        return sorted(all_risks, key=lambda x: x["score"], reverse=True)[:limit]
    def get_assessments(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._assessments[-limit:]
    def count(self) -> int:
        return len(self._assessments)
    def average_risk(self) -> float:
        if not self._assessments:
            return 0.0
        return sum(a["overall_risk"] for a in self._assessments) / len(self._assessments)
