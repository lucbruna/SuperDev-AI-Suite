from __future__ import annotations

from typing import Any


class InferenceRepository:
    """Repository for storing inference results."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def save(self, key: str, value: Any) -> None:
        self._store[key] = value

    async def load(self, key: str) -> Any | None:
        return self._store.get(key)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def list_keys(self) -> list[str]:
        return list(self._store.keys())

    async def search(self, query: str) -> list[tuple[str, Any]]:
        return [(k, v) for k, v in self._store.items() if query.lower() in k.lower()]
