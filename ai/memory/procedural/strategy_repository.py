from __future__ import annotations

from typing import Any


class Strategy:
    """A stored strategy definition."""

    def __init__(self, strategy_id: str, name: str, approach: str, steps: list[str], conditions: dict[str, Any] | None = None):
        self._strategy_id = strategy_id
        self._name = name
        self._approach = approach
        self._steps = list(steps)
        self._conditions = conditions or {}

    @property
    def strategy_id(self) -> str:
        return self._strategy_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def approach(self) -> str:
        return self._approach

    @property
    def steps(self) -> list[str]:
        return list(self._steps)

    @property
    def conditions(self) -> dict[str, Any]:
        return dict(self._conditions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self._strategy_id,
            "name": self._name,
            "approach": self._approach,
            "steps": list(self._steps),
            "conditions": dict(self._conditions),
        }


class StrategyRepository:
    """Repository of reusable strategies."""

    def __init__(self):
        self._strategies: dict[str, Strategy] = {}

    @property
    def count(self) -> int:
        return len(self._strategies)

    def add(self, strategy: Strategy) -> None:
        self._strategies[strategy.strategy_id] = strategy

    def get(self, strategy_id: str) -> Strategy | None:
        return self._strategies.get(strategy_id)

    def get_by_approach(self, approach: str) -> list[Strategy]:
        return [s for s in self._strategies.values() if s.approach == approach]

    def remove(self, strategy_id: str) -> bool:
        return self._strategies.pop(strategy_id, None) is not None

    def clear(self) -> None:
        self._strategies.clear()
