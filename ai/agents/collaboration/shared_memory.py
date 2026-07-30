from __future__ import annotations

from typing import Any, Dict, List, Optional


class SharedMemory:
    """Shared memory across agents."""

    def __init__(self) -> None:
        self._memory: Dict[str, Any] = {}

    @property
    def key_count(self) -> int:
        return len(self._memory)

    def store(self, key: str, value: Any) -> None:
        self._memory[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        return self._memory.get(key)

    def delete(self, key: str) -> bool:
        return self._memory.pop(key, None) is not None

    def keys(self) -> List[str]:
        return list(self._memory.keys())

    def clear(self) -> None:
        self._memory.clear()

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._memory)
