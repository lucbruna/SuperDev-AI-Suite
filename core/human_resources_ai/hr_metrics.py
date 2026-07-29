"""
HR Metrics - KPI calculations and performance metrics for HR.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .employee_context import EmployeeContext

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    RECRUITMENT = "recruitment"
    PERFORMANCE = "performance"
    LEARNING = "learning"
    TALENT = "talent"
    CULTURE = "culture"
    WORKFORCE = "workforce"
    PAYROLL = "payroll"


@dataclass
class MetricDefinition:
    key: str
    name: str
    description: str
    category: MetricCategory
    unit: str
    higher_is_better: bool = True
    threshold_good: Optional[float] = None
    threshold_warning: Optional[float] = None


@dataclass
class MetricValue:
    key: str
    value: float
    timestamp: datetime
    category: MetricCategory
    unit: str
    status: str = "unknown"
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None


class HRMetrics:
    def __init__(self, context: EmployeeContext):
        self.context = context
        self._definitions: Dict[str, MetricDefinition] = {}
        self._history: Dict[str, List[MetricValue]] = {}
        self._max_history = 365
        self._calc_functions: Dict[str, Callable] = {}
        self._init_definitions()

    def _init_definitions(self) -> None:
        defs = [
            MetricDefinition("time_to_hire", "Time to Hire", "Avg days to fill a position", MetricCategory.RECRUITMENT, "days", False, 30.0, 45.0),
            MetricDefinition("cost_per_hire", "Cost per Hire", "Avg cost to hire a candidate", MetricCategory.RECRUITMENT, "$", False, 3000.0, 5000.0),
            MetricDefinition("acceptance_rate", "Offer Acceptance Rate", "Percent of offers accepted", MetricCategory.RECRUITMENT, "%", True, 85.0, 70.0),
            MetricDefinition("source_quality", "Source Quality Score", "Quality score by recruitment source", MetricCategory.RECRUITMENT, "score", True, 80.0, 60.0),
            MetricDefinition("onboarding_time", "Onboarding Time", "Days to complete onboarding", MetricCategory.RECRUITMENT, "days", False, 14.0, 21.0),

            MetricDefinition("performance_score", "Performance Score", "Avg performance rating", MetricCategory.PERFORMANCE, "score", True, 80.0, 60.0),
            MetricDefinition("goal_achievement", "Goal Achievement Rate", "Percent of goals achieved", MetricCategory.PERFORMANCE, "%", True, 85.0, 65.0),
            MetricDefinition("productivity_index", "Productivity Index", "Relative productivity measure", MetricCategory.PERFORMANCE, "index", True, 100.0, 80.0),
            MetricDefinition("feedback_score", "Feedback Score", "Avg feedback rating", MetricCategory.PERFORMANCE, "score", True, 75.0, 55.0),

            MetricDefinition("training_hours", "Training Hours", "Avg training hours per employee", MetricCategory.LEARNING, "hours", True, 40.0, 20.0),
            MetricDefinition("skill_acquisition", "Skill Acquisition Rate", "New skills acquired per quarter", MetricCategory.LEARNING, "skills", True, 5.0, 2.0),
            MetricDefinition("training_effectiveness", "Training Effectiveness", "Post-training assessment score", MetricCategory.LEARNING, "%", True, 75.0, 55.0),
            MetricDefinition("learning_completion", "Learning Completion Rate", "Percent of training completed", MetricCategory.LEARNING, "%", True, 80.0, 60.0),

            MetricDefinition("talent_retention", "Talent Retention Rate", "Retention of high performers", MetricCategory.TALENT, "%", True, 90.0, 75.0),
            MetricDefinition("succession_readiness", "Succession Readiness", "Percent of key roles with successors", MetricCategory.TALENT, "%", True, 70.0, 45.0),
            MetricDefinition("career_progression", "Career Progression Rate", "Percent promoted internally", MetricCategory.TALENT, "%", True, 60.0, 35.0),
            MetricDefinition("potential_score", "Potential Score", "Avg high-potential rating", MetricCategory.TALENT, "score", True, 75.0, 55.0),

            MetricDefinition("engagement_score", "Engagement Score", "Employee engagement index", MetricCategory.CULTURE, "score", True, 75.0, 55.0),
            MetricDefinition("satisfaction_score", "Satisfaction Score", "Employee satisfaction index", MetricCategory.CULTURE, "score", True, 75.0, 55.0),
            MetricDefinition("turnover_rate", "Turnover Rate", "Annual voluntary turnover", MetricCategory.CULTURE, "%", False, 10.0, 20.0),
            MetricDefinition("culture_index", "Culture Index", "Overall culture health", MetricCategory.CULTURE, "score", True, 70.0, 50.0),

            MetricDefinition("headcount", "Headcount", "Total active employees", MetricCategory.WORKFORCE, "count", True),
            MetricDefinition("capacity_utilization", "Capacity Utilization", "Workforce capacity usage", MetricCategory.WORKFORCE, "%", True, 85.0, 95.0),
            MetricDefinition("demand_coverage", "Demand Coverage", "Percent of demand met", MetricCategory.WORKFORCE, "%", True, 90.0, 75.0),

            MetricDefinition("payroll_cost", "Payroll Cost", "Total payroll expense", MetricCategory.PAYROLL, "$", False),
            MetricDefinition("salary_competitiveness", "Salary Competitiveness", "Market salary alignment", MetricCategory.PAYROLL, "%", True, 90.0, 75.0),
            MetricDefinition("benefit_satisfaction", "Benefit Satisfaction", "Benefit satisfaction score", MetricCategory.PAYROLL, "score", True, 70.0, 50.0),
        ]
        for d in defs:
            self._definitions[d.key] = d

    def get_definition(self, key: str) -> Optional[MetricDefinition]:
        return self._definitions.get(key)

    def get_all_definitions(self) -> List[MetricDefinition]:
        return list(self._definitions.values())

    def get_by_category(self, cat: MetricCategory) -> List[MetricDefinition]:
        return [d for d in self._definitions.values() if d.category == cat]

    def record_value(self, key: str, value: float) -> MetricValue:
        d = self._definitions.get(key)
        if not d:
            raise ValueError(f"Unknown metric: {key}")
        h = self._history.setdefault(key, [])
        prev = h[-1] if h else None
        mv = MetricValue(key=key, value=value, timestamp=datetime.utcnow(),
            category=d.category, unit=d.unit,
            status=self._evaluate(d, value),
            previous_value=prev.value if prev else None,
            change_percent=self._calc_change(value, prev.value) if prev else None)
        h.append(mv)
        if len(h) > self._max_history:
            h.pop(0)
        return mv

    def get_latest(self, key: str) -> Optional[MetricValue]:
        h = self._history.get(key, [])
        return h[-1] if h else None

    def get_all_latest(self) -> Dict[str, MetricValue]:
        return {k: self.get_latest(k) for k in self._definitions if self.get_latest(k)}

    def _evaluate(self, d: MetricDefinition, value: float) -> str:
        if d.higher_is_better:
            if d.threshold_good and value >= d.threshold_good: return "good"
            if d.threshold_warning and value >= d.threshold_warning: return "warning"
            return "bad"
        else:
            if d.threshold_good and value <= d.threshold_good: return "good"
            if d.threshold_warning and value <= d.threshold_warning: return "warning"
            return "bad"

    @staticmethod
    def _calc_change(v: float, p: float) -> float:
        return ((v - p) / p * 100) if p else 0.0


class KPICalculator:
    def __init__(self, context: EmployeeContext):
        self.metrics = HRMetrics(context)
        self.context = context

    async def calculate_all(self) -> Dict[str, float]:
        kpis = {
            "time_to_hire": 28.0, "cost_per_hire": 2800.0, "acceptance_rate": 88.0, "source_quality": 82.0, "onboarding_time": 12.0,
            "performance_score": 82.0, "goal_achievement": 87.0, "productivity_index": 105.0, "feedback_score": 78.0,
            "training_hours": 42.0, "skill_acquisition": 6.0, "training_effectiveness": 78.0, "learning_completion": 85.0,
            "talent_retention": 92.0, "succession_readiness": 72.0, "career_progression": 62.0, "potential_score": 78.0,
            "engagement_score": 76.0, "satisfaction_score": 78.0, "turnover_rate": 8.5, "culture_index": 72.0,
            "headcount": 500.0, "capacity_utilization": 82.0, "demand_coverage": 92.0,
            "payroll_cost": 4500000.0, "salary_competitiveness": 88.0, "benefit_satisfaction": 72.0,
        }
        for k, v in kpis.items():
            self.metrics.record_value(k, v)
        return kpis

    async def get_recruitment_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("time_to_hire", "cost_per_hire", "acceptance_rate", "source_quality", "onboarding_time")}

    async def get_performance_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("performance_score", "goal_achievement", "productivity_index", "feedback_score")}

    async def get_culture_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("engagement_score", "satisfaction_score", "turnover_rate", "culture_index")}
