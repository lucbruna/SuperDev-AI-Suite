"""Inventory engine."""

import uuid
from datetime import datetime

from .models import InventoryItem, MovementType, ReplenishmentAlert, StockMovement, StockStatus


class InventoryEngine:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}
        self._movements: list[StockMovement] = []
        self._alerts: list[ReplenishmentAlert] = []

    def add_item(self, item: InventoryItem) -> InventoryItem:
        self._items[item.item_id] = item
        self._update_status(item)
        return item

    def get_item(self, item_id: str) -> InventoryItem | None:
        return self._items.get(item_id)

    def list_items(self, status: StockStatus | None = None) -> list[InventoryItem]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i.status == status]
        return items

    def record_movement(self, movement: StockMovement) -> StockMovement:
        item = self._items.get(movement.item_id)
        if item:
            if movement.movement_type == MovementType.IN:
                item.quantity += movement.quantity
            elif movement.movement_type == MovementType.OUT or movement.movement_type == MovementType.TRANSFER:
                item.quantity = max(0, item.quantity - movement.quantity)
            item.last_updated = datetime.now()
            self._update_status(item)
        self._movements.append(movement)
        return movement

    def get_movements(self, item_id: str | None = None) -> list[StockMovement]:
        if item_id:
            return [m for m in self._movements if m.item_id == item_id]
        return list(self._movements)

    def get_low_stock_items(self) -> list[InventoryItem]:
        return [i for i in self._items.values() if i.quantity <= i.min_quantity]

    def check_replenishment(self) -> list[ReplenishmentAlert]:
        alerts = []
        for item in self._items.values():
            if item.quantity <= item.min_quantity:
                suggested = item.max_quantity - item.quantity
                alert = ReplenishmentAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    item_id=item.item_id,
                    current_quantity=item.quantity,
                    min_required=item.min_quantity,
                    suggested_order=suggested,
                    priority="high" if item.quantity == 0 else "medium",
                )
                alerts.append(alert)
                self._alerts.append(alert)
        return alerts

    def _update_status(self, item: InventoryItem) -> None:
        if item.quantity == 0:
            item.status = StockStatus.OUT_OF_STOCK
        elif item.quantity <= item.min_quantity:
            item.status = StockStatus.LOW_STOCK
        elif item.quantity >= item.max_quantity:
            item.status = StockStatus.OVERSTOCKED
        else:
            item.status = StockStatus.IN_STOCK

    def get_stats(self) -> dict:
        items = list(self._items.values())
        total_value = sum(i.quantity * i.cost for i in items)
        low = [i for i in items if i.status == StockStatus.LOW_STOCK]
        return {
            "total_items": len(items),
            "total_stock": sum(i.quantity for i in items),
            "total_value": total_value,
            "low_stock_count": len(low),
            "movements": len(self._movements),
        }
