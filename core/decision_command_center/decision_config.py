from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class DashboardConfig:
    auto_refresh: bool = True
    default_refresh_seconds: int = 60
    max_widgets_per_dashboard: int = 20
    enable_realtime: bool = True
    enable_export: bool = True
    max_dashboards_per_user: int = 10


@dataclass
class AnalyticsConfig:
    enable_pattern_detection: bool = True
    enable_correlation: bool = True
    min_correlation_threshold: float = 0.5
    analysis_depth: str = "deep"
    max_patterns_per_analysis: int = 50


@dataclass
class PredictionConfig:
    enable_revenue_forecast: bool = True
    enable_demand_forecast: bool = True
    enable_risk_prediction: bool = True
    forecast_horizon_days: int = 365
    confidence_threshold: float = 0.7
    historical_data_months: int = 24


@dataclass
class SimulationConfig:
    enable_scenario_analysis: bool = True
    enable_impact_analysis: bool = True
    max_scenarios_per_session: int = 10
    simulation_timeout_seconds: int = 120
    default_time_horizon: str = "12m"


@dataclass
class RecommendationsConfig:
    enable_auto_recommendations: bool = True
    enable_action_planning: bool = True
    enable_priority_scoring: bool = True
    enable_optimization: bool = True
    min_impact_threshold: float = 0.3
    max_recommendations_per_analysis: int = 10


@dataclass
class ExecutiveConfig:
    enable_ceo_assistant: bool = True
    enable_board_reports: bool = True
    enable_strategic_summaries: bool = True
    report_frequency: str = "weekly"
    auto_distribution: bool = False


@dataclass
class IntegrationConfig:
    enable_erp_sync: bool = True
    enable_finance_sync: bool = True
    enable_crm_sync: bool = True
    enable_data_platform: bool = True
    enable_cybersecurity: bool = True
    enable_devops: bool = True
    enable_robotics: bool = True
    sync_interval_minutes: int = 15


@dataclass
class SecurityConfig:
    enable_access_control: bool = True
    enable_approval_workflow: bool = True
    enable_audit_trail: bool = True
    critical_decisions_require_approval: bool = True
    max_decision_levels: int = 3
    session_timeout_minutes: int = 30


@dataclass
class DecisionConfig:
    engine_name: str = "DecisionCommandCenter"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    enable_autonomous_decisions: bool = False
    enable_realtime_monitoring: bool = True
    enable_alerting: bool = True
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    prediction: PredictionConfig = field(default_factory=PredictionConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    recommendations: RecommendationsConfig = field(default_factory=RecommendationsConfig)
    executive: ExecutiveConfig = field(default_factory=ExecutiveConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DecisionConfig:
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
    def from_json(cls, path: str) -> DecisionConfig:
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
        if self.prediction.confidence_threshold < 0 or self.prediction.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
        if self.recommendations.min_impact_threshold < 0 or self.recommendations.min_impact_threshold > 1:
            errors.append("min_impact_threshold must be between 0 and 1")
        return errors
