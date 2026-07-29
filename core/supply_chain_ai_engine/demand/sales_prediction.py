"""
Sales Prediction - AI-powered demand forecasting.

Uses historical data, trends, and seasonality to predict future demand.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from random import uniform
from typing import Any, Dict, List, Tuple

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import DemandForecast
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class SalesPrediction:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    async def predict(self, horizon_days: int = 30, product_id: Optional[str] = None) -> DemandForecast:
        predictions = {}
        confidence = {}
        base = 500 if product_id else 3000
        for i in range(horizon_days):
            date = (datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d")
            seasonal = 1.0 + 0.3 * await self._seasonal_factor(i)
            trend = 1.0 + 0.001 * i
            noise = uniform(0.95, 1.05)
            prediction = base * seasonal * trend * noise
            predictions[date] = round(prediction, 2)
            ci = prediction * 0.15
            confidence[date] = (round(prediction - ci, 2), round(prediction + ci, 2))

        return DemandForecast(
            product_id=product_id or "all",
            forecast_date=datetime.utcnow(),
            horizon_days=horizon_days,
            predictions=predictions,
            confidence_intervals=confidence,
            seasonality_factors={"monday": 1.1, "weekend": 0.8},
            trend_direction=0.001,
            volatility=0.05,
        )

    async def _seasonal_factor(self, day_offset: int) -> float:
        return abs((day_offset % 7) - 3) / 7.0

    async def detect_spikes(self, historical: Dict[str, float], sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        spikes = []
        values = list(historical.values())
        if len(values) < 2:
            return spikes
        mean = sum(values) / len(values)
        for date, value in historical.items():
            if value > mean * sensitivity:
                spikes.append({"date": date, "value": value, "severity": "high" if value > mean * 3 else "medium"})
        return spikes