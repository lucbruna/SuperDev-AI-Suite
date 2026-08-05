"""Memory learning — persists and recalls directorial memory."""
from __future__ import annotations

from typing import Any


class MemoryLearning:
    """Stores key-value memory for the director."""

    def __init__(self) -> None:
        self._memory: dict[str, Any] = {}

    def remember(self, key: str, value: Any) -> None:
        self._memory[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self._memory.get(key, default)


_memory_learning: MemoryLearning | None = None


def get_memory_learning() -> MemoryLearning:
    global _memory_learning
    if _memory_learning is None:
        _memory_learning = MemoryLearning()
    return _memory_learning
