"""
Litigation Engine - Core litigation intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import LitigationCase, CaseStatus
from ..legal_config import LegalConfig
from .case_manager import CaseManager
from .deadline_tracker import DeadlineTracker
from .legal_prediction import LegalPrediction

logger = logging.getLogger(__name__)


class LitigationEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.cases: Optional[CaseManager] = None
        self.deadlines: Optional[DeadlineTracker] = None
        self.prediction: Optional[LegalPrediction] = None

    async def initialize(self) -> None:
        self.cases = CaseManager(self.config, self.context, self.event_bus)
        self.deadlines = DeadlineTracker(self.config, self.context, self.event_bus)
        self.prediction = LegalPrediction(self.config, self.context, self.event_bus)
        logger.info("LitigationEngine initialized")

    async def get_case(self, case_id: str) -> LitigationCase:
        return LitigationCase(id=case_id, title="Legal Case")

    async def open_case(self, title: str, parties: List[str]) -> LitigationCase:
        case = LitigationCase(id=f"LIT-{hash(title) % 10000:04d}", title=title, parties=parties)
        await self.event_bus.publish(LegalEvent(
            event_type=EventType.CASE_OPENED,
            payload={"case_id": case.id, "title": title},
        ))
        return case

    async def handle_deadline(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Litigation deadline handled: {payload}")

    async def shutdown(self) -> None:
        logger.info("LitigationEngine shutdown")
