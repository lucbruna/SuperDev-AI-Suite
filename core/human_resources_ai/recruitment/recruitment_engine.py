"""
Recruitment Engine - Core recruitment intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import CandidateProfile, JobPosition
from ..hr_config import HRConfig
from .candidate_analyzer import CandidateAnalyzer
from .resume_parser import ResumeParser
from .skill_matcher import SkillMatcher
from .interview_assistant import InterviewAssistant

logger = logging.getLogger(__name__)


class RecruitmentEngine:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.analyzer: Optional[CandidateAnalyzer] = None
        self.parser: Optional[ResumeParser] = None
        self.matcher: Optional[SkillMatcher] = None
        self.interview: Optional[InterviewAssistant] = None

    async def initialize(self) -> None:
        self.analyzer = CandidateAnalyzer(self.config, self.context, self.event_bus)
        self.parser = ResumeParser(self.config, self.context, self.event_bus)
        self.matcher = SkillMatcher(self.config, self.context, self.event_bus)
        self.interview = InterviewAssistant(self.config, self.context, self.event_bus)
        logger.info("RecruitmentEngine initialized")

    async def get_profile(self, candidate_id: str) -> CandidateProfile:
        return CandidateProfile(id=candidate_id, name="Unknown", match_score=85.0)

    async def screen(self, job_id: str, candidate_data: Dict[str, Any]) -> CandidateProfile:
        profile = CandidateProfile(
            id=candidate_data.get("id", "C-001"),
            name=candidate_data.get("name", "Unknown"),
            match_score=85.0,
        )
        await self.event_bus.publish(HREvent(
            event_type=EventType.CANDIDATE_SCREENED,
            payload={"candidate_id": profile.id, "score": profile.match_score},
        ))
        return profile

    async def handle_match(self, payload: Dict[str, Any]) -> None:
        logger.info(f"Match handled: {payload}")

    async def shutdown(self) -> None:
        logger.info("RecruitmentEngine shutdown")
