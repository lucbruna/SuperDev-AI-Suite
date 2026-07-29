from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import ProductionOrder

logger = logging.getLogger(__name__)


class ProcessController:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._orders: Dict[str, ProductionOrder] = {}

    async def start(self, order: ProductionOrder) -> ProductionOrder:
        order.id = str(uuid.uuid4())
        order.status = "running"
        order.start_time = datetime.utcnow()
        self._orders[order.id] = order
        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.PRODUCTION_STARTED,
            payload={"order_id": order.id, "product": order.product},
        ))
        return order

    async def stop(self, order_id: str) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.status = "completed"
        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.PRODUCTION_COMPLETED,
            payload={"order_id": order_id, "produced": order.produced, "defective": order.defective},
        ))
        return True

    async def record_production(self, order_id: str, quantity: int, defective: int = 0) -> Optional[ProductionOrder]:
        order = self._orders.get(order_id)
        if not order:
            return None
        order.produced += quantity
        order.defective += defective
        if defective > 0:
            await self.event_bus.publish(PhysicalEvent(
                event_type=EventType.PRODUCTION_DEFECT,
                payload={"order_id": order_id, "defective": defective},
            ))
        return order

    def get_order(self, order_id: str) -> Optional[ProductionOrder]:
        return self._orders.get(order_id)

    def get_active(self) -> List[ProductionOrder]:
        return [o for o in self._orders.values() if o.status == "running"]
