"""AI advisor subsystem for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from finance_intelligence.advisor.advisor_engine import AdvisorEngine
from finance_intelligence.advisor.insight_generator import InsightGenerator
from finance_intelligence.advisor.recommendation_engine import (
    RecommendationEngine)

__all__ = [
    "AdvisorEngine",
    "InsightGenerator",
    "RecommendationEngine",
]
