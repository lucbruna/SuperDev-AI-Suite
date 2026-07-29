"""
Compliance Engine - Core compliance intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import ComplianceReport, ComplianceStatus, ComplianceControl
from ..legal_config import LegalConfig
from .policy_checker import PolicyChecker
from .control_manager import ControlManager
from .compliance_report import ComplianceReportEngine

logger = logging.getLogger(__name__)


class ComplianceEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.policy_checker: Optional[PolicyChecker] = None
        self.controls: Optional[ControlManager] = None
        self.reporting: Optional[ComplianceReportEngine] = None

    async def initialize(self) -> None:
        self.policy_checker = PolicyChecker(self.config, self.context, self.event_bus)
        self.controls = ControlManager(self.config, self.context, self.event_bus)
        self.reporting = ComplianceReportEngine(self.config, self.context, self.event_bus)
        logger.info("ComplianceEngine initialized")

    async def get_report(self) -> ComplianceReport:
        return await self.reporting.generate()

    async def check(self, area: str = "all") -> ComplianceReport:
        report = await self.reporting.generate()
        if report.violations_count > 0:
            await self.event_bus.publish(LegalEvent(
                event_type=EventType.COMPLIANCE_VIOLATION,
                payload={"area": area, "violations": report.violations_count},
            ))
        return report

    async def check_all(self) -> ComplianceReport:
        return await self.reporting.generate()

    async def handle_violation(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Compliance violation handled: {payload}")

    async def generate_alert(self, alert_type: str) -> None:
        await self.event_bus.publish(LegalEvent(
            event_type=EventType.COMPLIANCE_VIOLATION,
            payload={"type": alert_type},
        ))

    async def shutdown(self) -> None:
        logger.info("ComplianceEngine shutdown")
