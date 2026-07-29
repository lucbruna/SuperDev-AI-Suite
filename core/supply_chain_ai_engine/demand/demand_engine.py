"""
Demand AI - Intelligent demand forecasting and analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import DemandForecast
from ..supply_config import SupplyChainConfig
from .sales_prediction import SalesPrediction
from .seasonality_analysis import SeasonalityAnalysis
from .market_analysis import MarketAnalysis

logger = logging.getLogger(__name__)


class DemandEngine:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.sales_prediction: Optional[SalesPrediction] = None
        self.seasonality: Optional[SeasonalityAnalysis] = None
        self.market_analysis: Optional[MarketAnalysis] = None

    async def initialize(self) -> None:
        self.sales_prediction = SalesPrediction(self.config, self.context, self.event_bus)
        self.seasonality = SeasonalityAnalysis(self.config, self.context, self.event_bus)
        self.market_analysis = MarketAnalysis(self.config, self.context, self.event_bus)
        logger.info("DemandEngine initialized")

    async def warm_up(self) -> None:
        pass

    async def get_forecast(self, horizon_days: int = 30) -> DemandForecast:
        return await self.sales_prediction.predict(horizon_days)

    async def handle_spike(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Handling demand spike: {payload}")

    async def analyze_seasonality(self, product_id: str) -> Dict[str, Any]:
        return await self.seasonality.analyze(product_id)

    async def analyze_market_trends(self, category: str) -> Dict[str, Any]:
        return await self.market_analysis.analyze_trends(category)

    async def shutdown(self) -> None:
        logger.info("DemandEngine shutdown")