"""
Financial Audit Engine - Core audit intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import AuditReport
from ..financial_config import FinancialConfig
from .anomaly_detection import AnomalyDetection
from .compliance_check import ComplianceCheck
from .audit_report import AuditReportGenerator

logger = logging.getLogger(__name__)


class FinancialAuditEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.anomaly: Optional[AnomalyDetection] = None
        self.compliance: Optional[ComplianceCheck] = None
        self.report_generator: Optional[AuditReportGenerator] = None

    async def initialize(self) -> None:
        self.anomaly = AnomalyDetection(self.config, self.context, self.event_bus)
        self.compliance = ComplianceCheck(self.config, self.context, self.event_bus)
        self.report_generator = AuditReportGenerator(self.config, self.context, self.event_bus)
        logger.info("FinancialAuditEngine initialized")

    async def run(self, scope: Optional[Dict] = None) -> AuditReport:
        return await self.report_generator.generate(scope)

    async def investigate(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Investigating: {payload}")

    async def shutdown(self) -> None:
        logger.info("FinancialAuditEngine shutdown")