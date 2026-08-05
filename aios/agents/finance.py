"""FinanceAgent: deterministic budgeting, allocation and forecasting."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent


class FinanceAgent(BaseAgent):
    def __init__(self, name: str = "finance", **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="finance",
            capabilities=["budgeting", "forecasting", "cost_analysis"],
            description="Allocates budgets and analyzes costs",
            **kwargs,
        )

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        data = input_data if isinstance(input_data, dict) else {}
        budget = float(data.get("budget", context.get("budget", 1000.0)))
        items = list(data.get("items") or context.get("items", ["infrastructure", "marketing", "operations"]))
        if not items:
            items = ["operations"]
        per_item = round(budget / len(items), 2)
        allocations = {item: per_item for item in items}
        total = sum(allocations.values())
        return {
            "budget": budget,
            "allocations": allocations,
            "total_allocated": round(total, 2),
            "variance": round(budget - total, 2),
            "status": "balanced" if abs(budget - total) < 0.01 else "adjusted",
        }
