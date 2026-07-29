"""
Financial Risk Engine - Core risk intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_models import RiskAssessment, RiskLevel
from ..financial_config import FinancialConfig
from .fraud_detection import FraudDetection
from .credit_analysis import CreditAnalysis
from .risk_score import RiskScore

logger = logging.getLogger(__name__)


class FinancialRiskEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.fraud: Optional[FraudDetection] = None
        self.credit: Optional[CreditAnalysis] = None
        self.risk_score: Optional[RiskScore] = None

    async def initialize(self) -> None:
        self.fraud = FraudDetection(self.config, self.context, self.event_bus)
        self.credit = CreditAnalysis(self.config, self.context, self.event_bus)
        self.risk_score = RiskScore(self.config, self.context, self.event_bus)
        logger.info("FinancialRiskEngine initialized")

    async def assess(self) -> RiskAssessment:
        return await self.risk_score.assess()

    async def investigate_fraud(self, payload: Dict[str, Any]) -> None:
        logger.warning(f"Fraud investigation: {payload}")

    async def shutdown(self) -> None:
        logger.info("FinancialRiskEngine shutdown")