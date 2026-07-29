"""
Budget Engine - Core budget intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import BudgetReport
from ..financial_config import FinancialConfig
from .budget_creator import BudgetCreator
from .budget_monitor import BudgetMonitor
from .deviation_analysis import DeviationAnalysis

logger = logging.getLogger(__name__)


class BudgetEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.creator: Optional[BudgetCreator] = None
        self.monitor: Optional[BudgetMonitor] = None
        self.deviation: Optional[DeviationAnalysis] = None

    async def initialize(self) -> None:
        self.creator = BudgetCreator(self.config, self.context, self.event_bus)
        self.monitor = BudgetMonitor(self.config, self.context, self.event_bus)
        self.deviation = DeviationAnalysis(self.config, self.context, self.event_bus)
        logger.info("BudgetEngine initialized")

    async def get_report(self, period: str = "monthly") -> BudgetReport:
        return await self.monitor.get_report(period)

    async def handle_deviation(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Budget deviation: {payload}")

    async def shutdown(self) -> None:
        logger.info("BudgetEngine shutdown")