"""Inventory."""

from __future__ import annotations

import time
from typing import Any


class InventoryManager:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def add(self, item_id: str, name: str, item_type: str, metadata: dict[str, Any] = None) -> dict[str, Any]:
        item = {
            "item_id": item_id,
            "name": name,
            "type": item_type,
            "metadata": metadata or {},
            "status": "active",
            "added_at": time.time(),
        }
        self._items[item_id] = item
        return item

    def get(self, item_id: str) -> dict[str, Any]:
        return self._items.get(item_id, {"error": "not_found"})

    def update(self, item_id: str, **kwargs: Any) -> bool:
        if item_id not in self._items:
            return False
        self._items[item_id].update(kwargs)
        return True

    def remove(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def list_by_type(self, item_type: str) -> list[dict[str, Any]]:
        return [i for i in self._items.values() if i.get("type") == item_type]

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._items.values())

    def count(self) -> int:
        return len(self._items)
