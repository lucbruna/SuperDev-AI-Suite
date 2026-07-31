"""BI Models — Core data models for business intelligence."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class DataSourceType(Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    WAREHOUSE = "warehouse"
    SPREADSHEET = "spreadsheet"


class AnalysisType(Enum):
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    RATIO = "ratio"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"


class DecisionType(Enum):
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    MARKETING = "marketing"
    SALES = "sales"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DataSource:
    source_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    source_type: DataSourceType = DataSourceType.DATABASE
    connection_string: str = ""
    schema: Dict[str, str] = field(default_factory=dict)
    refresh_interval: int = 300
    last_refreshed: Optional[datetime] = None
    active: bool = True


@dataclass
class DataPoint:
    point_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    metric_name: str = ""
    value: float = 0.0
    dimensions: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KPI:
    kpi_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    metric_type: MetricType = MetricType.RATIO
    target: float = 0.0
    current: float = 0.0
    unit: str = ""
    category: str = ""
    trend: str = "stable"
    threshold_warning: float = 0.0
    threshold_critical: float = 0.0

    @property
    def achievement(self) -> float:
        return (self.current / self.target * 100) if self.target != 0 else 0.0

    @property
    def status(self) -> str:
        if self.current >= self.target:
            return "on_track"
        elif self.current >= self.threshold_warning:
            return "warning"
        return "critical"


@dataclass
class Insight:
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    analysis_type: AnalysisType = AnalysisType.DESCRIPTIVE
    confidence: float = 0.0
    impact: str = "medium"
    data_points: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Prediction:
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target_metric: str = ""
    predicted_value: float = 0.0
    confidence_interval: tuple = (0.0, 0.0)
    horizon: str = ""
    model_used: str = ""
    accuracy: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Decision:
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    decision_type: DecisionType = DecisionType.STRATEGIC
    context: str = ""
    options: List[Dict[str, Any]] = field(default_factory=list)
    recommendation: str = ""
    confidence: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    expected_impact: str = ""
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Report:
    report_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    report_type: str = ""
    content: str = ""
    sections: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    author: str = "BI Engine"
