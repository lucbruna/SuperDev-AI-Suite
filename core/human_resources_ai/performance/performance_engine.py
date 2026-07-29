"""
Performance Engine - Core performance intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import PerformanceReview, PerformanceRating, Goal
from ..hr_config import HRConfig
from .goal_tracker import GoalTracker
from .productivity_analysis import ProductivityAnalysis
from .feedback_manager import FeedbackManager

logger = logging.getLogger(__name__)


class PerformanceEngine:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.goals: Optional[GoalTracker] = None
        self.productivity: Optional[ProductivityAnalysis] = None
        self.feedback: Optional[FeedbackManager] = None

    async def initialize(self) -> None:
        self.goals = GoalTracker(self.config, self.context, self.event_bus)
        self.productivity = ProductivityAnalysis(self.config, self.context, self.event_bus)
        self.feedback = FeedbackManager(self.config, self.context, self.event_bus)
        logger.info("PerformanceEngine initialized")

    async def get_review(self, employee_id: str) -> PerformanceReview:
        return PerformanceReview(
            id="R-001", employee_id=employee_id, reviewer_id="MGR-001",
            period="2026-Q2", overall_score=85.0,
            rating=PerformanceRating.EXCEEDS,
        )

    async def conduct_review(self, employee_id: str, reviewer_id: str) -> PerformanceReview:
        review = PerformanceReview(
            id=f"R-{employee_id}", employee_id=employee_id,
            reviewer_id=reviewer_id, period="2026-Q2",
            overall_score=82.0, rating=PerformanceRating.MEETS,
        )
        await self.event_bus.publish(HREvent(
            event_type=EventType.REVIEW_COMPLETED,
            payload={"employee_id": employee_id, "score": review.overall_score},
        ))
        return review

    async def investigate(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Performance investigation: {payload}")

    async def shutdown(self) -> None:
        logger.info("PerformanceEngine shutdown")
