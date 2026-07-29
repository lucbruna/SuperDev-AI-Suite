"""
Inventory Engine - Core inventory intelligence coordinator.

Coordinates stock monitoring, optimization, reordering, and analysis subsystems.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import InventoryItem, InventorySnapshot, StockStatus
from ..supply_config import SupplyChainConfig
from .stock_monitor import StockMonitor
from .stock_optimizer import StockOptimizer
from .reorder_manager import ReorderManager
from .inventory_analysis import InventoryAnalysis

logger = logging.getLogger(__name__)


class InventoryEngine:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.monitor: Optional[StockMonitor] = None
        self.optimizer: Optional[StockOptimizer] = None
        self.reorder_manager: Optional[ReorderManager] = None
        self.analysis: Optional[InventoryAnalysis] = None

    async def initialize(self) -> None:
        self.monitor = StockMonitor(self.config, self.context, self.event_bus)
        self.optimizer = StockOptimizer(self.config, self.context, self.event_bus)
        self.reorder_manager = ReorderManager(self.config, self.context, self.event_bus)
        self.analysis = InventoryAnalysis(self.config, self.context, self.event_bus)
        await self.monitor.initialize()
        logger.info("InventoryEngine initialized")

    async def warm_up(self) -> None:
        pass

    async def get_current_snapshot(self) -> InventorySnapshot:
        return await self.monitor.get_snapshot()

    async def handle_low_stock(self, payload: Dict[str, Any]) -> None:
        await self.reorder_manager.handle_low_stock(payload)

    async def adjust_for_delay(self, payload: Dict[str, Any]) -> None:
        product_id = payload.get("product_id")
        delay_days = payload.get("delay_days", 1)
        if product_id:
            await self.monitor.adjust_for_delay(product_id, delay_days)

    async def optimize_levels(self) -> Dict[str, Any]:
        snapshot = await self.get_current_snapshot()
        return await self.optimizer.optimize_levels(snapshot)

    async def analyze_turnover(self) -> Dict[str, float]:
        snapshot = await self.get_current_snapshot()
        return await self.analysis.analyze_turnover(snapshot)

    async def analyze_waste(self) -> Dict[str, Any]:
        snapshot = await self.get_current_snapshot()
        return await self.analysis.analyze_waste(snapshot)

    async def shutdown(self) -> None:
        logger.info("InventoryEngine shutdown")