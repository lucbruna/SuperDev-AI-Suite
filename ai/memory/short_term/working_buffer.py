from __future__ import annotations

from collections import deque
from typing import Any


class WorkingBuffer:
    """Fast in-memory buffer for active processing context."""

    def __init__(self, max_size: int = 100):
        self._max_size = max_size
        self._items: deque[Any] = deque(maxlen=max_size)
        self._metadata: dict[str, Any] = {}

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def size(self) -> int:
        return len(self._items)

    @property
    def is_full(self) -> bool:
        return len(self._items) >= self._max_size

    def push(self, item: Any) -> None:
        self._items.append(item)

    def pop(self) -> Any | None:
        if not self._items:
            return None
        return self._items.pop()

    def peek(self) -> Any | None:
        if not self._items:
            return None
        return self._items[-1]

    def peek_first(self) -> Any | None:
        if not self._items:
            return None
        return self._items[0]

    def items(self) -> list[Any]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()
        self._metadata.clear()

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_size": self._max_size,
            "current_size": len(self._items),
            "metadata": dict(self._metadata),
        }
