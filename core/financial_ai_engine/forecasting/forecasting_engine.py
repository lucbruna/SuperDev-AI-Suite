"""
Forecasting Engine - Core financial forecasting coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_config import FinancialConfig
from .revenue_prediction import RevenuePrediction
from .expense_prediction import ExpensePrediction
from .profitability_model import ProfitabilityModel

logger = logging.getLogger(__name__)


class ForecastingEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.revenue: Optional[RevenuePrediction] = None
        self.expense: Optional[ExpensePrediction] = None
        self.profitability: Optional[ProfitabilityModel] = None

    async def initialize(self) -> None:
        self.revenue = RevenuePrediction(self.config, self.context, self.event_bus)
        self.expense = ExpensePrediction(self.config, self.context, self.event_bus)
        self.profitability = ProfitabilityModel(self.config, self.context, self.event_bus)
        logger.info("ForecastingEngine initialized")

    async def get_forecast(self, horizon_days: int = 90) -> Dict[str, Any]:
        rev = await self.revenue.predict(horizon_days)
        exp = await self.expense.predict(horizon_days)
        prof = await self.profitability.analyze(rev, exp)
        return {"revenue": rev, "expense": exp, "profitability": prof}

    async def simulate(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        return await self.profitability.simulate(scenario)

    async def shutdown(self) -> None:
        logger.info("ForecastingEngine shutdown")