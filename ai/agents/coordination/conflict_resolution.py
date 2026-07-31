from __future__ import annotations

from typing import Any


class ConflictResolution:
    """Strategic conflict resolution for agents."""

    def __init__(self) -> None:
        self._strategies: dict[str, str] = {}
        self._history: list[dict[str, Any]] = []

    def add_strategy(self, conflict_type: str, strategy: str) -> None:
        self._strategies[conflict_type] = strategy

    def get_strategy(self, conflict_type: str) -> str | None:
        return self._strategies.get(conflict_type)

    def resolve(self, conflict_type: str, details: dict[str, Any]) -> str:
        strategy = self._strategies.get(conflict_type, "compromise")
        resolution = f"resolved_via_{strategy}"
        self._history.append({"type": conflict_type, "strategy": strategy, "details": details})
        return resolution

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def clear(self) -> None:
        self._strategies.clear()
        self._history.clear()
