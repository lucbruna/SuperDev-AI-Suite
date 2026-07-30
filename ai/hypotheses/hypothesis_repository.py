from __future__ import annotations

from typing import Any


class HypothesisRepository:
    """Persistent storage for hypotheses."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def save(self, hypothesis: dict[str, Any]) -> None:
        self._store[hypothesis.get("id", "")] = hypothesis

    async def load(self, hypothesis_id: str) -> dict[str, Any] | None:
        return self._store.get(hypothesis_id)

    async def delete(self, hypothesis_id: str) -> None:
        self._store.pop(hypothesis_id, None)

    async def list_all(self) -> list[dict[str, Any]]:
        return list(self._store.values())

    async def search(self, query: str) -> list[dict[str, Any]]:
        return [v for v in self._store.values() if query.lower() in str(v).lower()]
