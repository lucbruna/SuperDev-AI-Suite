"""
Investment Engine - Core investment intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import InvestmentAnalysis
from ..financial_config import FinancialConfig
from .opportunity_analysis import OpportunityAnalysis
from .return_calculator import ReturnCalculator
from .portfolio_manager import PortfolioManager

logger = logging.getLogger(__name__)


class InvestmentEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.opportunity: Optional[OpportunityAnalysis] = None
        self.returns: Optional[ReturnCalculator] = None
        self.portfolio: Optional[PortfolioManager] = None

    async def initialize(self) -> None:
        self.opportunity = OpportunityAnalysis(self.config, self.context, self.event_bus)
        self.returns = ReturnCalculator(self.config, self.context, self.event_bus)
        self.portfolio = PortfolioManager(self.config, self.context, self.event_bus)
        logger.info("InvestmentEngine initialized")

    async def analyze(self, opportunity: Dict[str, Any]) -> InvestmentAnalysis:
        return await self.opportunity.analyze(opportunity)

    async def shutdown(self) -> None:
        logger.info("InvestmentEngine shutdown")