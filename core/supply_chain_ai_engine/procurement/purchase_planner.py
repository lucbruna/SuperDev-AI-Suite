"""
Purchase Planner - Strategic purchase planning and optimization.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEventBus
from ..supply_models import ProcurementOrder, ProcurementPlan, OrderStatus
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class PurchasePlanner:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context

    async def create_plan(self, horizon_days: int = 30) -> ProcurementPlan:
        orders = [
            ProcurementOrder(
                id="PO-001", supplier_id="SUP-001",
                items={"cafe_500g": 500, "acucar_1kg": 300},
                estimated_cost=8000.0, status=OrderStatus.PLANNED,
                expected_delivery=datetime.utcnow() + timedelta(days=7),
            ),
            ProcurementOrder(
                id="PO-002", supplier_id="SUP-002",
                items={"leite_1l": 1000, "oleo_900ml": 400},
                estimated_cost=5500.0, status=OrderStatus.PLANNED,
                expected_delivery=datetime.utcnow() + timedelta(days=5),
            ),
        ]
        return ProcurementPlan(
            horizon_days=horizon_days, orders=orders,
            total_cost=13500.0, total_savings=450.0,
            risk_score=0.15,
            recommendations=["Consolidar pedidos de café e açúcar"],
        )

    async def consolidate_orders(self, orders: List[ProcurementOrder]) -> ProcurementOrder:
        items = {}
        total = 0.0
        for order in orders:
            items.update(order.items)
            total += order.estimated_cost
        return ProcurementOrder(
            id="PO-CONSOLIDATED", supplier_id=orders[0].supplier_id,
            items=items, estimated_cost=total * 0.9,
            status=OrderStatus.DRAFT,
        )

    async def calculate_economic_order_quantity(self, annual_demand: int, order_cost: float, holding_cost: float) -> int:
        return int((2 * annual_demand * order_cost / holding_cost) ** 0.5)