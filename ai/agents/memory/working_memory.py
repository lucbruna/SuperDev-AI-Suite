"""Working memory for active task context and focus."""

from __future__ import annotations

import time
from typing import Any


class WorkingMemory:
    """Active working memory for current task context and focus state."""

    def __init__(self, capacity: int = 7) -> None:
        self._capacity = capacity
        self._items: dict[str, dict[str, Any]] = {}
        self._focus_stack: list[str] = []
        self._context: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        if key in self._items:
            self._focus_stack.remove(key)
        elif len(self._items) >= self._capacity:
            oldest = self._focus_stack.pop(0)
            self._items.pop(oldest, None)
        self._items[key] = {
            "value": value,
            "timestamp": time.time(),
            "focus_count": self._items.get(key, {}).get("focus_count", 0) + 1,
        }
        self._focus_stack.append(key)

    def retrieve(self, key: str) -> Any | None:
        entry = self._items.get(key)
        if entry is None:
            return None
        if key in self._focus_stack:
            self._focus_stack.remove(key)
        self._focus_stack.append(key)
        return entry.get("value")

    def set_context(self, key: str, value: Any) -> None:
        self._context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    def clear_context(self) -> None:
        self._context.clear()

    def get_focused_items(self) -> list[str]:
        return list(reversed(self._focus_stack))

    def remove(self, key: str) -> bool:
        removed = key in self._items
        self._items.pop(key, None)
        if key in self._focus_stack:
            self._focus_stack.remove(key)
        return removed

    def count(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
        self._focus_stack.clear()
        self._context.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "items": len(self._items),
            "capacity": self._capacity,
            "focus_stack": list(self._focus_stack),
            "context_keys": list(self._context.keys()),
        }
