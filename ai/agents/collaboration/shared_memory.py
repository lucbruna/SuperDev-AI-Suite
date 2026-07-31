from __future__ import annotations

from typing import Any


class SharedMemory:
    """Shared memory across agents."""

    def __init__(self) -> None:
        self._memory: dict[str, Any] = {}

    @property
    def key_count(self) -> int:
        return len(self._memory)

    def store(self, key: str, value: Any) -> None:
        self._memory[key] = value

    def retrieve(self, key: str) -> Any | None:
        return self._memory.get(key)

    def delete(self, key: str) -> bool:
        return self._memory.pop(key, None) is not None

    def keys(self) -> list[str]:
        return list(self._memory.keys())

    def clear(self) -> None:
        self._memory.clear()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._memory)
