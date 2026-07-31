"""Risk prediction."""
from __future__ import annotations

from typing import Any


class RiskPredictor:
    def __init__(self) -> None:
        self._assessments: list[dict[str, Any]] = []
    def assess(self, scenario: dict[str, Any], risk_factors: list[str] = None) -> dict[str, Any]:
        risk_factors = risk_factors or ["financial", "operational", "strategic", "market"]
        risks = {}
        for factor in risk_factors:
            risks[factor] = {"probability": 0.3, "impact": 0.5, "score": 0.15}
        overall = sum(r["score"] for r in risks.values()) / len(risks) if risks else 0
        assessment = {"scenario": scenario, "risks": risks, "overall_risk": overall, "level": "medium" if overall < 0.5 else "high"}
        self._assessments.append(assessment)
        return assessment
    def get_highest_risks(self, limit: int = 5) -> list[dict[str, Any]]:
        all_risks = []
        for a in self._assessments:
            for factor, data in a.get("risks", {}).items():
                all_risks.append({"factor": factor, "score": data.get("score", 0), "assessment": a.get("scenario", {})})
        return sorted(all_risks, key=lambda x: x["score"], reverse=True)[:limit]
    def get_assessments(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._assessments[-limit:]
    def count(self) -> int:
        return len(self._assessments)
    def average_risk(self) -> float:
        if not self._assessments:
            return 0.0
        return sum(a["overall_risk"] for a in self._assessments) / len(self._assessments)
