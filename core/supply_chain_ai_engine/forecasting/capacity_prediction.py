"""
Capacity Prediction - Warehouse and operational capacity forecasting.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEventBus
from ..supply_models import CapacityPlan
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class CapacityPrediction:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config

    async def plan(self, horizon_days: int = 90) -> CapacityPlan:
        now = datetime.utcnow()
        return CapacityPlan(
            period_start=now, period_end=now + timedelta(days=horizon_days),
            current_capacity=5000.0, required_capacity=6200.0, capacity_gap=1200.0,
            expansion_recommended=True, expansion_cost=250000.0,
            recommendations=[
                "Expandir armazenagem em 25%",
                "Otimizar layout atual",
                "Considerar cross-docking",
            ],
        )

    async def predict_peak_demand(self, horizon_days: int = 90) -> Dict[str, Any]:
        return {
            "next_peak_date": datetime(2026, 12, 15),
            "expected_peak_capacity": 7500.0,
            "current_capacity": 5000.0,
            "gap": 2500.0,
            "preparation_needed": True,
        }

    async def calculate_capacity_utilization_trend(self) -> Dict[str, Any]:
        return {
            "current": 0.72,
            "forecast_30d": 0.78,
            "forecast_60d": 0.85,
            "forecast_90d": 0.92,
            "trend": "increasing",
            "warning_at": "60 days",
        }