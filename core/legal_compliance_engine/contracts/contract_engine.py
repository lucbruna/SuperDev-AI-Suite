"""
Contract Engine - Core contract intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEvent, LegalEventBus, EventType
from ..legal_models import Contract, ContractStatus, ContractType, Clause, RiskLevel
from ..legal_config import LegalConfig
from .contract_analyzer import ContractAnalyzer
from .clause_detector import ClauseDetector
from .obligation_tracker import ObligationTracker
from .contract_generator import ContractGenerator

logger = logging.getLogger(__name__)


class ContractEngine:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.analyzer: Optional[ContractAnalyzer] = None
        self.clause_detector: Optional[ClauseDetector] = None
        self.obligations: Optional[ObligationTracker] = None
        self.generator: Optional[ContractGenerator] = None

    async def initialize(self) -> None:
        self.analyzer = ContractAnalyzer(self.config, self.context, self.event_bus)
        self.clause_detector = ClauseDetector(self.config, self.context, self.event_bus)
        self.obligations = ObligationTracker(self.config, self.context, self.event_bus)
        self.generator = ContractGenerator(self.config, self.context, self.event_bus)
        logger.info("ContractEngine initialized")

    async def get_contract(self, contract_id: str) -> Contract:
        return Contract(id=contract_id, title="Sample Contract")

    async def analyze(self, contract_data: Dict[str, Any]) -> Contract:
        contract = Contract(
            id=contract_data.get("id", "CT-001"),
            title=contract_data.get("title", "Unknown"),
            value=contract_data.get("value", 0.0),
        )
        await self.event_bus.publish(LegalEvent(
            event_type=EventType.CONTRACT_RECEIVED,
            payload={"contract_id": contract.id, "title": contract.title},
        ))
        return contract

    async def handle_high_risk(self, payload: Dict[str, Any]) -> None:
        logger.info(f"High risk contract handled: {payload}")

    async def shutdown(self) -> None:
        logger.info("ContractEngine shutdown")
