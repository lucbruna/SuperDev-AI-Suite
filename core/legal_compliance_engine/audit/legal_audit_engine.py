"""
Legal Audit Engine - Core legal audit intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import AuditReport, AuditFinding
from ..legal_config import LegalConfig
from .evidence_manager import EvidenceManager
from .history_tracker import HistoryTracker
from .audit_report import AuditReportEngine

logger = logging.getLogger(__name__)


class LegalAuditEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.evidence: Optional[EvidenceManager] = None
        self.history: Optional[HistoryTracker] = None
        self.reporting: Optional[AuditReportEngine] = None

    async def initialize(self) -> None:
        self.evidence = EvidenceManager(self.config, self.context, self.event_bus)
        self.history = HistoryTracker(self.config, self.context, self.event_bus)
        self.reporting = AuditReportEngine(self.config, self.context, self.event_bus)
        logger.info("LegalAuditEngine initialized")

    async def run(self, scope: Optional[Dict] = None) -> AuditReport:
        report = await self.reporting.generate(scope or {})
        await self.event_bus.publish(LegalEvent(
            event_type=EventType.AUDIT_COMPLETED,
            payload={"report_id": report.report_id, "findings": report.total_findings},
        ))
        return report

    async def shutdown(self) -> None:
        logger.info("LegalAuditEngine shutdown")
