"""
Supplier Score - Supplier scoring and rating system.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEventBus
from ..supply_models import SupplierEvaluation
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class SupplierScore:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config

    async def evaluate(self, supplier_id: str) -> SupplierEvaluation:
        scores = {
            "SUP-001": SupplierEvaluation(supplier_id="SUP-001", supplier_name="Fornecedor A",
                overall_score=85, price_score=80, quality_score=90, delivery_score=85,
                reliability_score=88, risk_score=15,
                recommendations=["Manter contrato", "Negociar volume"]),
            "SUP-002": SupplierEvaluation(supplier_id="SUP-002", supplier_name="Fornecedor B",
                overall_score=72, price_score=85, quality_score=70, delivery_score=65,
                reliability_score=75, risk_score=35,
                recommendations=["Acompanhar performance", "Avaliar alternativas"]),
        }
        return scores.get(supplier_id, SupplierEvaluation(
            supplier_id=supplier_id, supplier_name="Desconhecido", overall_score=50))

    async def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        weights = {"price": 0.2, "quality": 0.3, "delivery": 0.25, "reliability": 0.15, "risk": 0.1}
        return sum(scores.get(k, 0) * w for k, w in weights.items())