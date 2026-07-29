"""
Supplier Engine - Core supplier intelligence management.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import Supplier, SupplierEvaluation, SupplierRiskLevel, SupplierStatus
from ..supply_config import SupplyChainConfig
from .supplier_score import SupplierScore
from .performance_analysis import PerformanceAnalysis
from .risk_analysis import RiskAnalysis

logger = logging.getLogger(__name__)


class SupplierEngine:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.scorer: Optional[SupplierScore] = None
        self.performance: Optional[PerformanceAnalysis] = None
        self.risk: Optional[RiskAnalysis] = None

    async def initialize(self) -> None:
        self.scorer = SupplierScore(self.config, self.context, self.event_bus)
        self.performance = PerformanceAnalysis(self.config, self.context, self.event_bus)
        self.risk = RiskAnalysis(self.config, self.context, self.event_bus)
        logger.info("SupplierEngine initialized")

    async def warm_up(self) -> None:
        pass

    async def get_all_status(self) -> Dict[str, Any]:
        return {"total": 5, "active": 4, "risky": 1}

    async def get_all_evaluations(self) -> List[SupplierEvaluation]:
        return [
            SupplierEvaluation(supplier_id="SUP-001", supplier_name="Fornecedor A", overall_score=85.0,
                               price_score=80.0, quality_score=90.0, delivery_score=85.0,
                               reliability_score=88.0, risk_score=15.0),
            SupplierEvaluation(supplier_id="SUP-002", supplier_name="Fornecedor B", overall_score=72.0,
                               price_score=85.0, quality_score=70.0, delivery_score=65.0,
                               reliability_score=75.0, risk_score=35.0),
        ]

    async def evaluate(self, supplier_id: str) -> SupplierEvaluation:
        return await self.scorer.evaluate(supplier_id)

    async def assess_risk(self, supplier_id: str) -> Dict[str, Any]:
        return await self.risk.assess(supplier_id)

    async def handle_risk(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Handling supplier risk: {payload}")

    async def find_alternatives(self, product_id: str, exclude: Optional[List[str]] = None) -> List[Supplier]:
        return [
            Supplier(id="ALT-001", name="Alternativa 1", contact_email="alt1@email.com"),
            Supplier(id="ALT-002", name="Alternativa 2", contact_email="alt2@email.com"),
        ]

    async def shutdown(self) -> None:
        logger.info("SupplierEngine shutdown")