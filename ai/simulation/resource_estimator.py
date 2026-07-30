from __future__ import annotations

from typing import Any


class ResourceEstimator:
    """Estimates resource requirements for scenarios."""

    def __init__(self) -> None:
        self._resource_prices: dict[str, float] = {"cpu": 0.10, "memory": 0.05, "storage": 0.02}

    def set_price(self, resource: str, price: float) -> None:
        self._resource_prices[resource] = price

    async def estimate(self, scenario: dict[str, Any]) -> dict[str, Any]:
        resources = scenario.get("resources", {})
        estimates = {}
        total_cost = 0.0
        for res, amount in resources.items():
            price = self._resource_prices.get(res, 0.01)
            cost = amount * price
            estimates[res] = {"amount": amount, "unit_cost": price, "total": round(cost, 2)}
            total_cost += cost
        return {"resources": estimates, "total_cost": round(total_cost, 2)}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        scenario = context.get("scenario", {})
        return await self.estimate(scenario)
