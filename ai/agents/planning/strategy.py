"""Strategy engine for selecting planning approaches."""
from __future__ import annotations

from typing import Any


class StrategyEngine:
    """Selects and applies planning strategies based on goal characteristics."""

    STRATEGIES = {
        "sequential": {"description": "Execute tasks one by one", "parallel": False},
        "parallel": {"description": "Execute independent tasks concurrently", "parallel": True},
        "divide_and_conquer": {"description": "Split into sub-problems", "parallel": True},
        "iterative": {"description": "Refine through repeated passes", "parallel": False},
        "greedy": {"description": "Pick highest-value task first", "parallel": False},
        "critical_path": {"description": "Focus on longest dependency chain", "parallel": False},
    }

    def __init__(self) -> None:
        self._custom_strategies: dict[str, dict[str, Any]] = {}

    def select_strategy(self, goal: str, tasks: list[dict[str, Any]],
                        context: dict[str, Any] | None = None) -> str:
        if not tasks:
            return "sequential"
        has_deps = any(t.get("dependencies") for t in tasks)
        task_count = len(tasks)
        if task_count > 5 and not has_deps:
            return "parallel"
        if has_deps and task_count > 3:
            return "critical_path"
        if task_count > 3:
            return "divide_and_conquer"
        return "sequential"

    def get_strategy(self, name: str) -> dict[str, Any] | None:
        return self.STRATEGIES.get(name) or self._custom_strategies.get(name)

    def register_strategy(self, name: str, config: dict[str, Any]) -> None:
        self._custom_strategies[name] = config

    def list_strategies(self) -> list[str]:
        return list(self.STRATEGIES.keys()) + list(self._custom_strategies.keys())

    def snapshot(self) -> dict[str, Any]:
        return {"strategies": self.list_strategies()}
