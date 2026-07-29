from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_security import DecisionSecurityManager
from .ceo_assistant import CEOAssistant
from .board_report import BoardReportGenerator
from .strategic_summary import StrategicSummary

logger = logging.getLogger(__name__)


class ExecutiveEngine:
    def __init__(self, config: DecisionConfig, security: DecisionSecurityManager):
        self.config = config
        self.security = security
        self.ceo: Optional[CEOAssistant] = None
        self.board: Optional[BoardReportGenerator] = None
        self.summary: Optional[StrategicSummary] = None

    async def initialize(self) -> None:
        self.ceo = CEOAssistant(self.config)
        self.board = BoardReportGenerator(self.config)
        self.summary = StrategicSummary(self.config)
        logger.info("ExecutiveEngine initialized")

    async def generate_summary(self) -> Dict[str, Any]:
        return self.summary.generate()

    async def generate_board_report(self) -> Dict[str, Any]:
        return self.board.generate()

    async def ceo_query(self, question: str) -> Dict[str, Any]:
        return self.ceo.answer(question)

    async def get_strategic_overview(self) -> Dict[str, Any]:
        return {
            "summary": self.summary.generate(),
            "board_highlights": self.board.get_highlights(),
        }

    async def shutdown(self) -> None:
        logger.info("ExecutiveEngine shutdown")
