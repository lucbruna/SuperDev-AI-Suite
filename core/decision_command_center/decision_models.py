from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class BusinessArea(Enum):
    FINANCIAL = "financial"
    OPERATIONS = "operations"
    SALES = "sales"
    MARKETING = "marketing"
    HR = "hr"
    LEGAL = "legal"
    CUSTOMER = "customer"
    SUPPLY_CHAIN = "supply_chain"
    IT = "it"
    STRATEGY = "strategy"


class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class InsightType(Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    CORRELATION = "correlation"
    PREDICTION = "prediction"


class ScenarioType(Enum):
    WHAT_IF = "what_if"
    FORECAST = "forecast"
    SIMULATION = "simulation"
    OPTIMIZATION = "optimization"


class RecommendationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DashboardType(Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    STRATEGIC = "strategic"
    CUSTOM = "custom"


class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    TABLE = "table"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"


@dataclass
class KPI:
    id: str
    name: str
    value: float = 0.0
    target: float = 0.0
    unit: str = ""
    trend: str = "stable"
    category: str = ""
    business_area: BusinessArea = BusinessArea.STRATEGY
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    status: str = "unknown"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    history: List[float] = field(default_factory=list)


@dataclass
class KpiGroup:
    id: str
    name: str
    kpis: List[KPI] = field(default_factory=list)
    overall_score: float = 0.0
    business_area: BusinessArea = BusinessArea.STRATEGY


@dataclass
class BusinessIndicator:
    id: str
    name: str
    value: float = 0.0
    baseline: float = 0.0
    min_threshold: float = 0.0
    max_threshold: float = 0.0
    unit: str = ""
    direction: str = "higher_is_better"
    category: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Insight:
    id: str
    title: str
    description: str
    insight_type: InsightType = InsightType.TREND
    severity: AlertSeverity = AlertSeverity.INFO
    business_area: BusinessArea = BusinessArea.STRATEGY
    confidence: float = 0.0
    impact_score: float = 0.0
    related_kpis: List[str] = field(default_factory=list)
    source: str = ""
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False


@dataclass
class Scenario:
    id: str
    name: str
    scenario_type: ScenarioType = ScenarioType.WHAT_IF
    parameters: Dict[str, Any] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    projected_impact: Dict[str, float] = field(default_factory=dict)
    risk_level: str = "medium"
    confidence: float = 0.0
    time_horizon: str = "12m"
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"


@dataclass
class Recommendation:
    id: str
    title: str
    description: str
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    business_area: BusinessArea = BusinessArea.STRATEGY
    expected_impact: Dict[str, float] = field(default_factory=dict)
    required_resources: Dict[str, Any] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    roi_estimate: float = 0.0
    effort_hours: int = 0
    status: DecisionStatus = DecisionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_by: str = ""
    decision_rationale: str = ""


@dataclass
class ActionPlan:
    id: str
    title: str
    recommendations: List[Recommendation] = field(default_factory=list)
    total_effort_hours: int = 0
    total_roi: float = 0.0
    priority_score: float = 0.0
    status: DecisionStatus = DecisionStatus.PENDING
    owner: str = ""
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Dashboard:
    id: str
    name: str
    dashboard_type: DashboardType = DashboardType.OPERATIONAL
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_interval_seconds: int = 60
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_refreshed: Optional[datetime] = None


@dataclass
class Widget:
    id: str
    title: str
    chart_type: ChartType = ChartType.BAR
    data_source: str = ""
    kpi_ids: List[str] = field(default_factory=list)
    width: int = 2
    height: int = 2
    position_x: int = 0
    position_y: int = 0
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    id: str
    title: str
    message: str
    severity: AlertSeverity = AlertSeverity.INFO
    business_area: BusinessArea = BusinessArea.STRATEGY
    source: str = ""
    related_kpi: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class Prediction:
    id: str
    metric: str
    current_value: float = 0.0
    predicted_value: float = 0.0
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    confidence: float = 0.0
    time_horizon: str = "30d"
    factors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueForecast:
    id: str
    period: str
    projected_revenue: float = 0.0
    projected_cost: float = 0.0
    projected_profit: float = 0.0
    confidence: float = 0.0
    scenarios: Dict[str, float] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Correlation:
    id: str
    variable_a: str
    variable_b: str
    coefficient: float = 0.0
    strength: str = "none"
    direction: str = "positive"
    description: str = ""
    business_area: BusinessArea = BusinessArea.STRATEGY


@dataclass
class Pattern:
    id: str
    name: str
    description: str
    frequency: str = "recurring"
    confidence: float = 0.0
    related_metrics: List[str] = field(default_factory=list)
    business_area: BusinessArea = BusinessArea.STRATEGY
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BenchmarkData:
    id: str
    metric: str
    company_value: float = 0.0
    industry_average: float = 0.0
    best_in_class: float = 0.0
    percentile: float = 0.0
    gap: float = 0.0
    business_area: BusinessArea = BusinessArea.STRATEGY
    period: str = "2026-Q2"


@dataclass
class ExecutiveSummary:
    id: str
    title: str
    period: str
    overview: str = ""
    key_highlights: List[str] = field(default_factory=list)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    opportunities: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    kpi_summary: Dict[str, float] = field(default_factory=dict)
    overall_health: str = "good"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BoardReport:
    id: str
    title: str
    quarter: str
    year: int = 2026
    sections: Dict[str, Any] = field(default_factory=dict)
    financial_summary: Dict[str, float] = field(default_factory=dict)
    strategic_initiatives: List[Dict[str, Any]] = field(default_factory=list)
    risk_overview: List[Dict[str, Any]] = field(default_factory=list)
    outlook: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DecisionLog:
    id: str
    decision: str
    rationale: str
    impact: Dict[str, Any] = field(default_factory=dict)
    status: DecisionStatus = DecisionStatus.PENDING
    recommended_by: str = "ai"
    approved_by: str = ""
    business_area: BusinessArea = BusinessArea.STRATEGY
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None


@dataclass
class SimulationResult:
    id: str
    scenario_id: str
    projected_outcomes: Dict[str, float] = field(default_factory=dict)
    risks_identified: List[str] = field(default_factory=list)
    feasibility_score: float = 0.0
    recommendation: str = ""
    confidence: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
