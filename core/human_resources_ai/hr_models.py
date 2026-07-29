"""
HR Models - Core human resources data models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class EmploymentStatus(Enum):
    ACTIVE = "active"
    PROBATION = "probation"
    NOTICE = "notice"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class ContractType(Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    INTERN = "intern"
    TEMPORARY = "temporary"
    PART_TIME = "part_time"


class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PerformanceRating(Enum):
    EXCEPTIONAL = 5
    EXCEEDS = 4
    MEETS = 3
    BELOW = 2
    UNSATISFACTORY = 1


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Employee:
    id: str
    name: str
    email: str
    department: str = ""
    position: str = ""
    status: EmploymentStatus = EmploymentStatus.ACTIVE
    contract_type: ContractType = ContractType.PERMANENT
    manager_id: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Skill:
    name: str
    category: str = ""
    level: SkillLevel = SkillLevel.INTERMEDIATE
    years_experience: float = 0.0


@dataclass
class JobPosition:
    id: str
    title: str
    department: str
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    experience_years_min: int = 0
    salary_range_min: float = 0.0
    salary_range_max: float = 0.0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CandidateProfile:
    id: str
    name: str
    email: str = ""
    position_applied: str = ""
    match_score: float = 0.0
    compatibility_percent: float = 0.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    skills: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    status: str = "new"
    recommendation: str = ""
    interviewed: bool = False
    source: str = ""
    applied_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class InterviewFeedback:
    candidate_id: str
    interviewer: str
    technical_score: float = 0.0
    communication_score: float = 0.0
    cultural_fit_score: float = 0.0
    overall_score: float = 0.0
    notes: str = ""
    recommendation: str = ""
    conducted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OnboardingPlan:
    employee_id: str
    employee_name: str
    position: str
    duration_days: int = 30
    phases: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"
    start_date: datetime = field(default_factory=datetime.utcnow)
    completion_date: Optional[datetime] = None
    buddy_id: Optional[str] = None


@dataclass
class TrainingModule:
    id: str
    title: str
    description: str = ""
    category: str = ""
    duration_hours: float = 0.0
    required: bool = False
    skills_covered: List[str] = field(default_factory=list)


@dataclass
class Goal:
    id: str
    employee_id: str
    title: str
    description: str = ""
    target_value: float = 0.0
    current_value: float = 0.0
    unit: str = ""
    deadline: Optional[datetime] = None
    status: str = "active"
    category: str = ""
    weight: float = 1.0


@dataclass
class PerformanceReview:
    id: str
    employee_id: str
    reviewer_id: str
    period: str
    overall_score: float = 0.0
    goals_achieved_percent: float = 0.0
    productivity_score: float = 0.0
    feedback_score: float = 0.0
    rating: PerformanceRating = PerformanceRating.MEETS
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    comments: str = ""
    reviewed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LearningPath:
    employee_id: str
    employee_name: str
    position: str
    modules: List[TrainingModule] = field(default_factory=list)
    total_hours: float = 0.0
    progress_percent: float = 0.0
    status: str = "active"
    recommended_by: str = "AI"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TalentProfile:
    employee_id: str
    employee_name: str
    position: str
    skills: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    performance_history: List[float] = field(default_factory=list)
    potential_score: float = 0.0
    leadership_score: float = 0.0
    career_goals: List[str] = field(default_factory=list)
    recommended_next_role: str = ""
    succession_ready: bool = False
    retention_risk: RiskLevel = RiskLevel.LOW
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CareerPath:
    employee_id: str
    current_role: str
    target_role: str
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    estimated_time_months: int = 12
    progress_percent: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SuccessionPlan:
    position_id: str
    position_title: str
    candidates: List[str] = field(default_factory=list)
    readiness_scores: Dict[str, float] = field(default_factory=dict)
    criticality: str = "medium"
    last_reviewed: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CultureReport:
    period: str
    engagement_score: float = 0.0
    satisfaction_score: float = 0.0
    turnover_rate: float = 0.0
    culture_index: float = 0.0
    survey_responses: int = 0
    sentiment_trend: str = "stable"
    department_scores: Dict[str, float] = field(default_factory=dict)
    top_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class EngagementSurvey:
    id: str
    department: str
    overall_score: float = 0.0
    communication_score: float = 0.0
    leadership_score: float = 0.0
    growth_score: float = 0.0
    wellbeing_score: float = 0.0
    responses: int = 0
    conducted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkforcePlan:
    period: str
    total_headcount: int = 0
    active_headcount: int = 0
    open_positions: int = 0
    projected_hires: int = 0
    projected_attrition: int = 0
    capacity_utilization: float = 0.0
    department_plans: Dict[str, Any] = field(default_factory=dict)
    skills_gap: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ShiftSchedule:
    employee_id: str
    date: str
    start_time: str = ""
    end_time: str = ""
    department: str = ""
    role: str = ""
    is_overtime: bool = False


@dataclass
class PayrollSummary:
    period: str
    total_employees: int = 0
    total_gross_pay: float = 0.0
    total_deductions: float = 0.0
    total_net_pay: float = 0.0
    total_benefits_cost: float = 0.0
    total_employer_taxes: float = 0.0
    average_salary: float = 0.0
    median_salary: float = 0.0
    department_breakdown: Dict[str, Any] = field(default_factory=dict)
    processed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SalaryAnalysis:
    position: str
    market_average: float = 0.0
    market_min: float = 0.0
    market_max: float = 0.0
    company_average: float = 0.0
    competitiveness_percent: float = 0.0
    adjustment_recommended: float = 0.0
    adjustment_percent: float = 0.0


@dataclass
class Benefit:
    id: str
    name: str
    type: str = ""
    cost_per_employee: float = 0.0
    employer_contribution: float = 0.0
    employee_contribution: float = 0.0
    is_mandatory: bool = False


@dataclass
class CompensationReview:
    employee_id: str
    current_salary: float = 0.0
    proposed_salary: float = 0.0
    adjustment_percent: float = 0.0
    reason: str = ""
    approved: bool = False
    effective_date: Optional[datetime] = None


@dataclass
class HRAction:
    id: str
    action_type: str
    description: str
    employee_id: str
    initiated_by: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class HRAlert:
    id: str
    alert_type: str
    severity: str
    title: str
    message: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
