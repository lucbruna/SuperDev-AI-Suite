"""
Candidate Analyzer - Deep candidate analysis beyond the resume.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREventBus
from ..hr_models import CandidateProfile, SkillLevel
from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class CandidateAnalyzer:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def analyze_experience(self, candidate: CandidateProfile) -> Dict[str, Any]:
        return {
            "total_years": candidate.experience_years,
            "relevant_years": candidate.experience_years * 0.8,
            "skill_depth": len(candidate.skills),
            "experience_score": min(candidate.experience_years / 10 * 100, 100),
        }

    def analyze_compatibility(self, candidate: CandidateProfile, position: str) -> float:
        return candidate.compatibility_percent or 85.0

    def generate_recommendation(self, candidate: CandidateProfile) -> str:
        if candidate.match_score >= 90:
            return "advanced_to_interview"
        elif candidate.match_score >= 70:
            return "review_further"
        return "not_recommended"
