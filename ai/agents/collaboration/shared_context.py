from __future__ import annotations

from typing import Any, Dict, Optional


class SharedContext:
    """Shared context accessible by all agents."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    @property
    def key_count(self) -> int:
        return len(self._data)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def remove(self, key: str) -> bool:
        return self._data.pop(key, None) is not None

    def clear(self) -> None:
        self._data.clear()

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
