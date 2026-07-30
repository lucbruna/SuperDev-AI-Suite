from __future__ import annotations

from typing import Any

from .decision_models import DecisionResult


class DecisionRepository:
    """Persistence for decision results."""

    def __init__(self):
        self._store: dict[str, DecisionResult] = {}

    def save(self, result: DecisionResult) -> None:
        self._store[result.context_id] = result

    def get(self, context_id: str) -> DecisionResult | None:
        return self._store.get(context_id)

    def list_all(self) -> list[DecisionResult]:
        return list(self._store.values())

    def delete(self, context_id: str) -> bool:
        return self._store.pop(context_id, None) is not None

    def clear(self) -> None:
        self._store.clear()
