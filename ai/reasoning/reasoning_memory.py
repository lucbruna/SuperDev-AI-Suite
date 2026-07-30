from __future__ import annotations

from typing import Any


class ReasoningMemory:
    """Short-term and long-term memory for reasoning context."""

    def __init__(self):
        self._short_term: dict[str, Any] = {}
        self._long_term: dict[str, Any] = {}

    async def store(self, key: str, value: Any, persistent: bool = False) -> None:
        if persistent:
            self._long_term[key] = value
        else:
            self._short_term[key] = value

    async def retrieve(self, key: str) -> Any | None:
        return self._short_term.get(key) or self._long_term.get(key)

    async def forget(self, key: str) -> bool:
        return self._short_term.pop(key, None) is not None or self._long_term.pop(key, None) is not None

    async def clear_short_term(self) -> None:
        self._short_term.clear()

    async def clear_all(self) -> None:
        self._short_term.clear()
        self._long_term.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "short_term_items": len(self._short_term),
            "long_term_items": len(self._long_term),
        }
