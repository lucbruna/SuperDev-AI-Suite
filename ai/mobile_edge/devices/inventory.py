"""Inventory - Device inventory management."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class InventoryItem:
    item_id: str
    name: str
    category: str = ""
    serial_number: str = ""
    model: str = ""
    manufacturer: str = ""
    purchase_date: datetime | None = None
    warranty_expires: datetime | None = None
    assigned_to: str = ""
    location: str = ""
    status: str = "available"
    metadata: dict[str, Any] = field(default_factory=dict)


class DeviceInventory:
    def __init__(self):
        self.items: dict[str, InventoryItem] = {}

    def add(self, item_id: str, name: str, **kwargs) -> InventoryItem:
        item = InventoryItem(item_id=item_id, name=name, **kwargs)
        self.items[item_id] = item
        return item

    def get(self, item_id: str) -> InventoryItem | None:
        return self.items.get(item_id)

    def update(self, item_id: str, **kwargs) -> bool:
        item = self.items.get(item_id)
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            return True
        return False

    def assign(self, item_id: str, user: str) -> bool:
        item = self.items.get(item_id)
        if item:
            item.assigned_to = user
            item.status = "assigned"
            return True
        return False

    def unassign(self, item_id: str) -> bool:
        item = self.items.get(item_id)
        if item:
            item.assigned_to = ""
            item.status = "available"
            return True
        return False

    def search(self, query: str) -> list[InventoryItem]:
        return [i for i in self.items.values() if query.lower() in i.name.lower() or query.lower() in i.model.lower()]

    def list_items(self, category: str = None, status: str = None) -> list[InventoryItem]:
        items = list(self.items.values())
        if category:
            items = [i for i in items if i.category == category]
        if status:
            items = [i for i in items if i.status == status]
        return items

    def count(self) -> int:
        return len(self.items)
