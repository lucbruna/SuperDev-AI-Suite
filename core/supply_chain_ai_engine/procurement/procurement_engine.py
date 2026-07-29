"""
Procurement Engine - Core procurement intelligence.

Coordinates purchase planning, price analysis, and negotiation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import ProcurementOrder, ProcurementPlan, OrderStatus
from ..supply_config import SupplyChainConfig
from .purchase_planner import PurchasePlanner
from .price_analysis import PriceAnalysis
from .negotiation_assistant import NegotiationAssistant

logger = logging.getLogger(__name__)


class ProcurementEngine:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.planner: Optional[PurchasePlanner] = None
        self.price_analysis: Optional[PriceAnalysis] = None
        self.negotiator: Optional[NegotiationAssistant] = None

    async def initialize(self) -> None:
        self.planner = PurchasePlanner(self.config, self.context, self.event_bus)
        self.price_analysis = PriceAnalysis(self.config, self.context, self.event_bus)
        self.negotiator = NegotiationAssistant(self.config, self.context, self.event_bus)
        logger.info("ProcurementEngine initialized")

    async def warm_up(self) -> None:
        pass

    async def get_plan(self, horizon_days: int = 30) -> ProcurementPlan:
        return await self.planner.create_plan(horizon_days)

    async def create_purchase_order(self, order: ProcurementOrder) -> ProcurementOrder:
        order.status = OrderStatus.PLACED
        await self.event_bus.publish(SupplyChainEvent(
            event_type=EventType.PROCUREMENT_ORDER_CREATED,
            payload={"order_id": order.id, "supplier": order.supplier_id},
        ))
        return order

    async def prepare_emergency_procurement(self, payload: Dict[str, Any]) -> None:
        await self.event_bus.publish(SupplyChainEvent(
            event_type=EventType.PROCUREMENT_EMERGENCY,
            payload=payload,
        ))

    async def find_alternative_suppliers(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"supplier_id": "ALT-001", "name": "Fornecedor Alternativo", "score": 85}]

    async def analyze_prices(self, product_id: str) -> Dict[str, Any]:
        return await self.price_analysis.analyze(product_id)

    async def shutdown(self) -> None:
        logger.info("ProcurementEngine shutdown")