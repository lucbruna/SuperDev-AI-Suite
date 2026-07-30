from __future__ import annotations

from typing import Any


class CostEstimator:
    """Estimates financial cost of simulation scenarios."""

    def __init__(self) -> None:
        self._cost_factors: dict[str, float] = {"compute": 1.0, "storage": 0.5, "bandwidth": 0.3}

    def set_factor(self, name: str, rate: float) -> None:
        self._cost_factors[name] = rate

    async def estimate(self, scenario: dict[str, Any]) -> dict[str, Any]:
        resources = scenario.get("resources", {})
        breakdown = {}
        total = 0.0
        for factor, rate in self._cost_factors.items():
            amount = resources.get(factor, 0)
            cost = amount * rate
            breakdown[factor] = {"amount": amount, "rate": rate, "cost": round(cost, 2)}
            total += cost
        return {
            "total_cost": round(total, 2),
            "breakdown": breakdown,
            "currency": "USD",
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        scenario = context.get("scenario", {})
        return await self.estimate(scenario)
