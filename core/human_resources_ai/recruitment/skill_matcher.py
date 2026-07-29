"""
Skill Matcher - Match candidate skills against job requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREventBus
from ..hr_models import CandidateProfile, Skill, SkillLevel
from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class SkillMatcher:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def match(self, candidate_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        matched = [s for s in candidate_skills if s in required_skills]
        missing = [s for s in required_skills if s not in candidate_skills]
        score = (len(matched) / max(len(required_skills), 1)) * 100
        return {
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "compatibility": "high" if score >= 80 else "medium" if score >= 50 else "low",
        }

    def calculate_compatibility(self, candidate: CandidateProfile, position_title: str) -> float:
        return candidate.compatibility_percent or 85.0
