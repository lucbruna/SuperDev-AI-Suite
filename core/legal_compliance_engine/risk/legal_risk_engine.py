"""
Legal Risk Engine - Core legal risk intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import RiskAssessment, RiskLevel
from ..legal_config import LegalConfig
from .risk_calculator import RiskCalculator
from .impact_analysis import ImpactAnalysis
from .mitigation import MitigationPlanner

logger = logging.getLogger(__name__)


class LegalRiskEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.calculator: Optional[RiskCalculator] = None
        self.impact: Optional[ImpactAnalysis] = None
        self.mitigation: Optional[MitigationPlanner] = None

    async def initialize(self) -> None:
        self.calculator = RiskCalculator(self.config, self.context, self.event_bus)
        self.impact = ImpactAnalysis(self.config, self.context, self.event_bus)
        self.mitigation = MitigationPlanner(self.config, self.context, self.event_bus)
        logger.info("LegalRiskEngine initialized")

    async def assess(self, context: Optional[Dict] = None) -> RiskAssessment:
        assessment = self.calculator.calculate(context or {})
        if assessment.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            await self.event_bus.publish(LegalEvent(
                event_type=EventType.RISK_THRESHOLD_EXCEEDED,
                payload={"score": assessment.overall_score, "level": assessment.risk_level.value},
            ))
        return assessment

    async def shutdown(self) -> None:
        logger.info("LegalRiskEngine shutdown")
