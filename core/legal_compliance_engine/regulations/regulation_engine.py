"""
Regulation Engine - Core regulatory intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import Regulation
from ..legal_config import LegalConfig
from .law_monitor import LawMonitor
from .regulation_tracker import RegulationTracker
from .update_analyzer import UpdateAnalyzer

logger = logging.getLogger(__name__)


class RegulationEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.monitor: Optional[LawMonitor] = None
        self.tracker: Optional[RegulationTracker] = None
        self.analyzer: Optional[UpdateAnalyzer] = None

    async def initialize(self) -> None:
        self.monitor = LawMonitor(self.config, self.context, self.event_bus)
        self.tracker = RegulationTracker(self.config, self.context, self.event_bus)
        self.analyzer = UpdateAnalyzer(self.config, self.context, self.event_bus)
        logger.info("RegulationEngine initialized")

    async def check_updates(self) -> List[Regulation]:
        updates = await self.monitor.check()
        for u in updates:
            await self.event_bus.publish(LegalEvent(
                event_type=EventType.REGULATION_CHANGED,
                payload={"regulation_id": u.id, "name": u.name},
            ))
        return updates

    async def handle_change(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Regulation change handled: {payload}")

    async def shutdown(self) -> None:
        logger.info("RegulationEngine shutdown")
