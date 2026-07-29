"""
Reorder Manager - Autonomous reorder management system.

Handles automatic reorder decisions, purchase order generation,
and replenishment optimization.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import ProcurementOrder, OrderStatus
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class ReorderManager:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._pending_reorders: List[Dict[str, Any]] = []

    async def handle_low_stock(self, payload: Dict[str, Any]) -> None:
        product_id = payload.get("product_id", "unknown")
        quantity = payload.get("quantity", 100)
        if self.config.inventory.auto_reorder_enabled:
            order = await self._create_reorder(product_id, quantity)
            await self.event_bus.publish(SupplyChainEvent(
                event_type=EventType.REPLENISHMENT_TRIGGERED,
                payload={"product_id": product_id, "quantity": quantity, "order_id": order.id},
            ))
            logger.info(f"Reorder triggered: {product_id} x{quantity}")

    async def check_reorder_needs(self, inventory_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        needs = []
        for product_id, item in inventory_data.items():
            if item.get("is_low", False):
                qty = item.get("optimal_level", 0) - item.get("current_stock", 0)
                if qty > 0:
                    needs.append({"product_id": product_id, "quantity": qty})
        return needs

    async def _create_reorder(self, product_id: str, quantity: int) -> ProcurementOrder:
        order = ProcurementOrder(
            id=f"REORDER-{product_id}-{hash(str(datetime.utcnow())) % 10000}",
            supplier_id="SUP-001",
            items={product_id: quantity},
            estimated_cost=quantity * 10.0,
            status=OrderStatus.APPROVED if self.config.inventory.auto_approve_reorder else OrderStatus.PENDING_APPROVAL,
            is_emergency=False,
        )
        self._pending_reorders.append({"order": order, "timestamp": datetime.utcnow()})
        return order

    async def get_pending_reorders(self) -> List[Dict[str, Any]]:
        return self._pending_reorders

    async def get_reorder_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._pending_reorders[-limit:]