"""Business Intelligence Analytics subsystem."""

from .config import AnalyticsConfig, DashboardConfig, ReportConfig
from .engine import AnalyticsEngine
from .interfaces import (
    AnalyticsEngineInterface,
    DashboardInterface,
    DataWarehouseInterface,
    ReportGeneratorInterface,
)
from .models import (
    AnalysisRequest,
    AnalysisResult,
    AnalysisType,
    DataPoint,
    Insight,
    InsightType,
    MetricType,
)

__all__ = [
    "AnalysisType",
    "MetricType",
    "InsightType",
    "DataPoint",
    "Insight",
    "AnalysisRequest",
    "AnalysisResult",
    "AnalyticsEngineInterface",
    "DataWarehouseInterface",
    "DashboardInterface",
    "ReportGeneratorInterface",
    "AnalyticsConfig",
    "DashboardConfig",
    "ReportConfig",
    "AnalyticsEngine",
]
