"""Hallmark cache — bounded result cache with LRU-ish eviction."""
from __future__ import annotations
from typing import Any, Hashable
from collections import OrderedDict


class ResultCache:
    """Store results keyed by hashable keys, evicting oldest beyond maxsize."""

    def __init__(self, maxsize: int = 128) -> None:
        self._maxsize = maxsize
        self._items: "OrderedDict[Hashable, Any]" = OrderedDict()

    def get(self, key: Hashable, default: Any = None) -> Any:
        if key not in self._items:
            return default
        self._items.move_to_end(key)
        return self._items[key]

    def set(self, key: Hashable, value: Any) -> None:
        if key in self._items:
            self._items.move_to_end(key)
        self._items[key] = value
        while len(self._items) > self._maxsize:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()

    def stats(self) -> dict[str, Any]:
        return {"size": len(self._items), "maxsize": self._maxsize}
