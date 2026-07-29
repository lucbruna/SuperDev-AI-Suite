"""
HR Configuration - Global HR AI engine configuration.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RecruitmentConfig:
    auto_screen: bool = True
    auto_shortlist: bool = True
    min_match_score: float = 70.0
    interview_stages: int = 3
    enable_skill_validation: bool = True
    default_source: str = "linkedin"


@dataclass
class OnboardingConfig:
    default_duration_days: int = 30
    auto_assign_buddy: bool = True
    training_required: bool = True
    checkpoints: List[str] = field(default_factory=lambda: ["day1", "week1", "week2", "month1"])
    document_verification_required: bool = True


@dataclass
class PerformanceConfig:
    review_frequency: str = "quarterly"
    enable_continuous_feedback: bool = True
    goal_tracking_enabled: bool = True
    productivity_analysis: bool = True
    rating_scale_max: int = 5
    auto_schedule_reviews: bool = True


@dataclass
class LearningConfig:
    enable_recommendations: bool = True
    enable_skill_tracking: bool = True
    enable_knowledge_paths: bool = True
    min_training_hours_per_year: float = 40.0
    certification_support: bool = True


@dataclass
class TalentConfig:
    enable_skill_graph: bool = True
    enable_career_planning: bool = True
    enable_succession: bool = True
    high_potential_threshold: float = 80.0
    succession_depth: int = 3


@dataclass
class CultureConfig:
    survey_frequency_days: int = 90
    enable_sentiment_analysis: bool = True
    enable_engagement_monitoring: bool = True
    engagement_warning_threshold: float = 55.0
    anonymous_surveys: bool = True


@dataclass
class WorkforceConfig:
    forecast_horizon_months: int = 12
    enable_demand_prediction: bool = True
    enable_scheduling: bool = True
    max_overtime_hours_per_week: int = 10
    capacity_warning_threshold: float = 90.0


@dataclass
class PayrollConfig:
    processing_frequency: str = "monthly"
    auto_calculate_taxes: bool = True
    auto_calculate_benefits: bool = True
    enable_salary_analysis: bool = True
    currency: str = "BRL"
    fiscal_year_start: str = "01-01"


@dataclass
class SecurityConfig:
    enable_encryption: bool = True
    enable_access_control: bool = True
    audit_trail_enabled: bool = True
    sensitive_fields: List[str] = field(default_factory=lambda: ["salary", "tax_id", "bank_account", "health_info", "evaluation"])
    session_timeout_minutes: int = 30


@dataclass
class IntegrationConfig:
    enable_erp_sync: bool = True
    enable_knowledge_sync: bool = True
    enable_crm_sync: bool = True
    knowledge_sync_interval_minutes: int = 60
    decision_center_enabled: bool = True


@dataclass
class HRConfig:
    engine_name: str = "HRAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    recruitment: RecruitmentConfig = field(default_factory=RecruitmentConfig)
    onboarding: OnboardingConfig = field(default_factory=OnboardingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    talent: TalentConfig = field(default_factory=TalentConfig)
    culture: CultureConfig = field(default_factory=CultureConfig)
    workforce: WorkforceConfig = field(default_factory=WorkforceConfig)
    payroll: PayrollConfig = field(default_factory=PayrollConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    enable_employee_digital_twin: bool = True
    enable_autonomous_hr: bool = True
    enable_continuous_learning: bool = True
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HRConfig":
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    sub = getattr(config, key)
                    if hasattr(sub, "__dataclass_fields__"):
                        for sk, sv in value.items():
                            if hasattr(sub, sk):
                                setattr(sub, sk, sv)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config

    @classmethod
    def from_json(cls, path: str) -> "HRConfig":
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def validate(self) -> List[str]:
        errors = []
        if self.recruitment.min_match_score < 0 or self.recruitment.min_match_score > 100:
            errors.append("min_match_score must be between 0 and 100")
        if self.onboarding.default_duration_days < 1:
            errors.append("default_duration_days must be >= 1")
        if self.culture.engagement_warning_threshold < 0:
            errors.append("engagement_warning_threshold must be positive")
        return errors
