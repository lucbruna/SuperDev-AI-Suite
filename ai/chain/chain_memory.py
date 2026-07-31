from __future__ import annotations

from typing import Any


class ChainMemory:
    """Stores and retrieves reasoning chain executions."""

    def __init__(self) -> None:
        self._store: list[dict[str, Any]] = []

    async def save(self, chain: dict[str, Any], result: dict[str, Any]) -> None:
        self._store.append(
            {
                "chain": chain,
                "result": result,
                "steps": len(chain.get("steps", [])),
            }
        )

    async def recall(self, query: str) -> list[dict[str, Any]]:
        return [s for s in self._store if query.lower() in str(s).lower()]

    async def recent(self, n: int = 5) -> list[dict[str, Any]]:
        return self._store[-n:]

    async def clear(self) -> None:
        self._store.clear()
