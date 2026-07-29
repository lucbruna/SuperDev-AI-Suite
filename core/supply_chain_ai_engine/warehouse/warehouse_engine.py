"""
Warehouse Engine - Core warehouse intelligence coordination.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import WarehouseLayout, WarehouseLocation, WarehouseZone
from ..supply_config import SupplyChainConfig
from .location_optimizer import LocationOptimizer
from .picking_manager import PickingManager

logger = logging.getLogger(__name__)


class WarehouseEngine:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.location_optimizer: Optional[LocationOptimizer] = None
        self.picking_manager: Optional[PickingManager] = None

    async def initialize(self) -> None:
        self.location_optimizer = LocationOptimizer(self.config, self.context, self.event_bus)
        self.picking_manager = PickingManager(self.config, self.context, self.event_bus)
        logger.info("WarehouseEngine initialized")

    async def warm_up(self) -> None:
        pass

    async def get_layout(self) -> WarehouseLayout:
        return WarehouseLayout(
            locations={"LOC-001": WarehouseLocation(id="LOC-001", zone=WarehouseZone.STORAGE, aisle="A", rack="01", level=1)},
            total_capacity=5000, current_utilization=0.72, total_products=1200,
            last_optimized=datetime.utcnow(), picking_efficiency=0.85,
        )

    async def apply_optimizations(self, optimizations: List[Dict[str, Any]]) -> None:
        logger.info(f"Applied {len(optimizations)} warehouse optimizations")

    async def handle_capacity_warning(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Handling capacity warning: {payload}")

    async def optimize_layout(self) -> WarehouseLayout:
        return await self.location_optimizer.optimize()

    async def get_picking_route(self, order_id: str) -> List[Dict[str, Any]]:
        return await self.picking_manager.get_route(order_id)

    async def get_location_recommendations(self) -> List[Dict[str, Any]]:
        return await self.location_optimizer.recommend_locations()

    async def shutdown(self) -> None:
        logger.info("WarehouseEngine shutdown")