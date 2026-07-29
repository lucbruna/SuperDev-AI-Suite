"""
Cashflow Engine - Core cash flow intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import CashflowForecast
from ..financial_config import FinancialConfig
from .inflow_analysis import InflowAnalysis
from .outflow_analysis import OutflowAnalysis
from .liquidity_prediction import LiquidityPrediction

logger = logging.getLogger(__name__)


class CashflowEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.inflows: Optional[InflowAnalysis] = None
        self.outflows: Optional[OutflowAnalysis] = None
        self.prediction: Optional[LiquidityPrediction] = None

    async def initialize(self) -> None:
        self.inflows = InflowAnalysis(self.config, self.context, self.event_bus)
        self.outflows = OutflowAnalysis(self.config, self.context, self.event_bus)
        self.prediction = LiquidityPrediction(self.config, self.context, self.event_bus)
        logger.info("CashflowEngine initialized")

    async def forecast(self, horizon_days: int = 90) -> CashflowForecast:
        return await self.prediction.forecast(horizon_days)

    async def shutdown(self) -> None:
        logger.info("CashflowEngine shutdown")