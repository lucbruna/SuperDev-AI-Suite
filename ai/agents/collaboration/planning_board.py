from __future__ import annotations

from typing import Any, Dict, List, Optional


class PlanningBoard:
    """Shared planning board for collaborative work."""

    def __init__(self) -> None:
        self._items: Dict[str, Dict[str, Any]] = {}

    @property
    def item_count(self) -> int:
        return len(self._items)

    def add_item(self, item_id: str, description: str, assignee: str = "") -> None:
        self._items[item_id] = {"description": description, "assignee": assignee, "status": "open"}

    def update_status(self, item_id: str, status: str) -> bool:
        item = self._items.get(item_id)
        if item:
            item["status"] = status
            return True
        return False

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        item = self._items.get(item_id)
        return dict(item) if item else None

    def list_items(self, status: str = "") -> List[Dict[str, Any]]:
        items = [dict(v) for v in self._items.values()]
        if status:
            items = [i for i in items if i["status"] == status]
        return items

    def remove_item(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def clear(self) -> None:
        self._items.clear()
