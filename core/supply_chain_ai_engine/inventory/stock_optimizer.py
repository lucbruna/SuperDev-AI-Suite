"""
Stock Optimizer - Intelligent stock level optimization.

Calculates optimal stock levels, safety stock, and reorder points
based on demand patterns and lead times.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEventBus
from ..supply_models import InventorySnapshot, StockStatus
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class StockOptimizer:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context

    async def optimize_levels(self, snapshot: InventorySnapshot) -> Dict[str, Any]:
        recommendations = {}
        for sku, item in snapshot.items.items():
            if item.status == StockStatus.EXCESS:
                recommendations[sku] = {
                    "action": "reduce_stock",
                    "current": item.current_stock,
                    "target": item.optimal_level,
                    "message": f"Excesso: reduzir de {item.current_stock} para {item.optimal_level}",
                }
            elif item.is_low:
                recommendations[sku] = {
                    "action": "reorder",
                    "current": item.current_stock,
                    "suggested_order": item.optimal_level - item.current_stock,
                    "message": f"Estoque baixo: reordenar {item.optimal_level - item.current_stock} unidades",
                }
        return {"recommendations": recommendations, "optimized": True}

    async def calculate_safety_stock(self, avg_daily_demand: float, lead_time_days: int, service_level: float = 0.95) -> int:
        z_score = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}.get(service_level, 1.65)
        demand_std = avg_daily_demand * 0.3
        return int(z_score * demand_std * (lead_time_days ** 0.5))

    async def calculate_reorder_point(self, avg_daily_demand: float, lead_time_days: int, safety_stock: int) -> int:
        return int(avg_daily_demand * lead_time_days) + safety_stock

    async def calculate_optimal_level(self, avg_daily_demand: float, lead_time_days: int, order_cycle_days: int = 30) -> int:
        return int(avg_daily_demand * (lead_time_days + order_cycle_days))