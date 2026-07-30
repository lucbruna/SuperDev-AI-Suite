from __future__ import annotations

from typing import Any


class RiskEstimator:
    """Estimates risk levels for simulation scenarios."""

    def __init__(self) -> None:
        self._risk_factors: list[dict[str, Any]] = []

    def add_factor(self, name: str, weight: float, threshold: float) -> None:
        self._risk_factors.append({"name": name, "weight": weight, "threshold": threshold})

    async def estimate(self, scenario: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        total_risk = 0.0
        factors: list[dict[str, Any]] = []
        for factor in self._risk_factors:
            value = scenario.get(factor["name"], 0)
            risk = min(1.0, value / factor["threshold"]) if factor["threshold"] > 0 else 0.5
            weighted = risk * factor["weight"]
            total_risk += weighted
            factors.append({"name": factor["name"], "risk": round(risk, 2), "weighted": round(weighted, 2)})
        success_rate = result.get("success_rate", 1.0)
        overall = min(1.0, total_risk + (1 - success_rate) * 0.5)
        return {
            "overall_risk": round(overall, 2),
            "risk_factors": factors,
            "level": "high" if overall > 0.7 else "medium" if overall > 0.3 else "low",
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        scenario = context.get("scenario", {})
        result = context.get("result", {})
        return await self.estimate(scenario, result)
