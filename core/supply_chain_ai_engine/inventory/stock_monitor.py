"""
Stock Monitor - Real-time inventory monitoring system.

Tracks stock levels, detects low stock and critical levels,
provides inventory snapshots.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import InventoryItem, InventorySnapshot, StockStatus
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class StockMonitor:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._stock_data: Dict[str, InventoryItem] = {}
        self._init_sample_data()

    def _init_sample_data(self) -> None:
        items = [
            ("cafe_500g", "Café 500g", 800, 0, 500, StockStatus.LOW_STOCK),
            ("arroz_5kg", "Arroz 5kg", 1500, 0, 300, StockStatus.IN_STOCK),
            ("feijao_1kg", "Feijão 1kg", 2000, 0, 400, StockStatus.IN_STOCK),
            ("acucar_1kg", "Açúcar 1kg", 50, 0, 200, StockStatus.CRITICAL),
            ("oleo_900ml", "Óleo 900ml", 1200, 0, 300, StockStatus.IN_STOCK),
            ("leite_1l", "Leite 1L", 30, 0, 500, StockStatus.CRITICAL),
            ("farinha_1kg", "Farinha 1kg", 600, 0, 250, StockStatus.IN_STOCK),
            ("sal_1kg", "Sal 1kg", 3000, 0, 200, StockStatus.EXCESS),
            ("macarrao_500g", "Macarrão 500g", 900, 0, 350, StockStatus.IN_STOCK),
            ("molho_tomate_340g", "Molho de Tomate 340g", 100, 0, 300, StockStatus.LOW_STOCK),
        ]
        for sku, name, stock, reserved, reorder, status in items:
            self._stock_data[sku] = InventoryItem(
                product_id=sku, sku=sku, product_name=name,
                current_stock=stock, reserved_stock=reserved,
                incoming_stock=50 if status in (StockStatus.LOW_STOCK, StockStatus.CRITICAL) else 0,
                status=status, reorder_point=reorder, optimal_level=reorder * 3,
                location=f"Aisle-{hash(sku) % 10}",
            )

    async def initialize(self) -> None:
        logger.info("StockMonitor initialized with %d products", len(self._stock_data))

    async def get_snapshot(self) -> InventorySnapshot:
        items = {sku: InventoryItem(
            product_id=item.product_id, sku=item.sku,
            product_name=item.product_name, current_stock=item.current_stock,
            reserved_stock=item.reserved_stock, available_stock=item.available,
            incoming_stock=item.incoming_stock, status=item.status,
            location=item.location, reorder_point=item.reorder_point,
            optimal_level=item.optimal_level,
        ) for sku, item in self._stock_data.items()}
        total_value = sum(i.current_stock * 10.0 for i in items.values())
        return InventorySnapshot(
            items=items, total_items=len(items), total_value=total_value,
            low_stock_count=sum(1 for i in items.values() if i.is_low),
            out_of_stock_count=sum(1 for i in items.values() if i.status == StockStatus.OUT_OF_STOCK),
            excess_count=sum(1 for i in items.values() if i.status == StockStatus.EXCESS),
        )

    async def get_item(self, product_id: str) -> Optional[InventoryItem]:
        return self._stock_data.get(product_id)

    async def update_stock(self, product_id: str, quantity: int, reason: str = "manual") -> bool:
        item = self._stock_data.get(product_id)
        if not item:
            return False
        item.current_stock = quantity
        item.status = self._determine_status(item)
        await self.event_bus.publish(SupplyChainEvent(
            event_type=EventType.INVENTORY_UPDATED,
            payload={"product_id": product_id, "new_quantity": quantity, "reason": reason},
        ))
        return True

    async def adjust_for_delay(self, product_id: str, delay_days: int) -> None:
        item = self._stock_data.get(product_id)
        if item:
            item.incoming_stock = 0
            item.status = StockStatus.CRITICAL
            await self.event_bus.publish(SupplyChainEvent(
                event_type=EventType.INVENTORY_CRITICAL,
                payload={"product_id": product_id, "reason": f"delay_{delay_days}d"},
            ))

    def _determine_status(self, item: InventoryItem) -> StockStatus:
        if item.current_stock <= 0:
            return StockStatus.OUT_OF_STOCK
        if item.current_stock <= item.reorder_point * 0.3:
            return StockStatus.CRITICAL
        if item.current_stock <= item.reorder_point:
            return StockStatus.LOW_STOCK
        if item.current_stock > item.optimal_level * 1.5:
            return StockStatus.EXCESS
        return StockStatus.IN_STOCK