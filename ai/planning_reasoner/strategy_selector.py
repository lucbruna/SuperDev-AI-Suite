from __future__ import annotations

from typing import Any


class StrategySelector:
    """Selects the best reasoning strategy based on objectives."""

    def __init__(self) -> None:
        self._strategies: dict[str, dict[str, Any]] = {}

    def register_strategy(self, name: str, config: dict[str, Any]) -> None:
        self._strategies[name] = config

    async def select(self, objectives: dict[str, Any]) -> dict[str, Any]:
        complexity = objectives.get("complexity", "low")
        if complexity == "high":
            return {"name": "deep_reasoning", "depth": 5, "complexity": complexity}
        if complexity == "medium":
            return {"name": "balanced", "depth": 3, "complexity": complexity}
        return {"name": "fast", "depth": 1, "complexity": complexity}
