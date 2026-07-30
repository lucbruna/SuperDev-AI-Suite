from __future__ import annotations

from typing import Any


class GoalOptimizer:
    """Optimizes plans to better achieve goals."""

    def __init__(self) -> None:
        self._optimizations: list[dict[str, Any]] = []

    def add_optimization(self, opt: dict[str, Any]) -> None:
        self._optimizations.append(opt)

    async def optimize(self, plan: dict[str, Any], objectives: dict[str, Any]) -> dict[str, Any]:
        steps = list(plan.get("steps", []))
        for opt in self._optimizations:
            action = opt.get("action", "")
            if action == "remove_redundant":
                steps = [s for s in steps if s.get("action") != "none"]
            if action == "prioritize":
                steps.sort(key=lambda s: s.get("priority", 0), reverse=True)
        return {**plan, "steps": steps, "optimized": True}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        plan = context.get("plan", {})
        objectives = context.get("objectives", {})
        return await self.optimize(plan, objectives)
