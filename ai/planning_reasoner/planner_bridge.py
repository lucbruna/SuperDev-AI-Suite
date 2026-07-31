from __future__ import annotations

from typing import Any


class PlannerBridge:
    """Bridge between reasoning and the planner module."""

    def __init__(self) -> None:
        self._strategies: dict[str, Any] = {}

    def register_strategy(self, name: str, strategy: Any) -> None:
        self._strategies[name] = strategy

    async def create_plan(self, context: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
        steps: list[dict[str, Any]] = []
        strategy_name = strategy.get("name", "default")
        if strategy_name in self._strategies:
            return await self._strategies[strategy_name](context)
        steps.append(
            {
                "id": "step_1",
                "action": "analyze",
                "description": "Analyze context and generate plan",
                "dependencies": [],
            }
        )
        return {"steps": steps, "strategy": strategy_name}
