"""In-memory event queue with async-style processing."""

from __future__ import annotations

from typing import Any, Callable


class EventQueue:
    """Buffers event deliveries and processes them in order."""

    def __init__(self) -> None:
        self._items: list[tuple[dict[str, Any], Callable[[dict[str, Any]], None]]] = []

    def enqueue(self, event: dict[str, Any],
                handler: Callable[[dict[str, Any]], None]) -> None:
        self._items.append((event, handler))

    def process(self, limit: int = 100) -> int:
        count = 0
        while self._items and count < limit:
            event, handler = self._items.pop(0)
            handler(event)
            count += 1
        return count

    def size(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
