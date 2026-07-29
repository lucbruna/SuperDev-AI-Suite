"""
Supply Forecaster - Core forecasting intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import RiskPrediction, CapacityPlan
from ..supply_config import SupplyChainConfig
from .risk_prediction import RiskPrediction as RiskPredictor
from .capacity_prediction import CapacityPrediction

logger = logging.getLogger(__name__)


class SupplyForecaster:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.risk_predictor: Optional[RiskPredictor] = None
        self.capacity_predictor: Optional[CapacityPrediction] = None

    async def initialize(self) -> None:
        self.risk_predictor = RiskPredictor(self.config, self.context, self.event_bus)
        self.capacity_predictor = CapacityPrediction(self.config, self.context, self.event_bus)
        logger.info("SupplyForecaster initialized")

    async def warm_up(self) -> None:
        pass

    async def plan_capacity(self, horizon_days: int = 90) -> CapacityPlan:
        return await self.capacity_predictor.plan(horizon_days)

    async def predict_risks(self, horizon_days: int = 30) -> List[RiskPrediction]:
        return await self.risk_predictor.predict(horizon_days)

    async def shutdown(self) -> None:
        logger.info("SupplyForecaster shutdown")