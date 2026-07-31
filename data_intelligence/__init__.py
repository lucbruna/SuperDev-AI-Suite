"""Data Intelligence & Analytics Engine (Volume 22).

Public API for collecting, organizing and analyzing data: ingestion,
pipelines, processing, warehouse, lake, analytics, visualization, machine
learning, forecasting, reporting and governance.
"""
from __future__ import annotations

from .data_config import DataIntelligenceConfig
from .data_context import DataIntelligenceContext
from .data_engine import DataIntelligenceEngine
from .data_events import DataIntelligenceEventType, DataIntelligenceEvents
from .data_factory import build_engine
from .data_interfaces import (AnalyticsProvider, DataConnector, DataSink,
                              ModelProvider, ReportGenerator)
from .data_logger import get_logger
from .data_manager import DataIntelligenceManager
from .data_metrics import DataIntelligenceMetrics
from .data_models import (AnalyticsLevel, AnalyticsResult, DashboardSpec,
                          DataClassification, DataRecord, DataSource,
                          GovernanceRecord, ModelRecord, ModelStatus,
                          PipelineSpec, PipelineStatus, PredictionResult,
                          ReportFormat, ReportSpec, SourceType)
from .data_protocols import coerce_bool, coerce_number, new_id, numeric_values, safe_get
from .data_registry import DataIntelligenceRegistry
from .data_runtime import DataIntelligenceRuntime
from .data_security import DataIntelligenceSecurity

__all__ = [
    "AnalyticsLevel",
    "AnalyticsProvider",
    "AnalyticsResult",
    "DashboardSpec",
    "DataClassification",
    "DataConnector",
    "DataIntelligenceConfig",
    "DataIntelligenceContext",
    "DataIntelligenceEngine",
    "DataIntelligenceEventType",
    "DataIntelligenceEvents",
    "DataIntelligenceManager",
    "DataIntelligenceMetrics",
    "DataIntelligenceRegistry",
    "DataIntelligenceRuntime",
    "DataIntelligenceSecurity",
    "DataRecord",
    "DataSource",
    "DataSink",
    "GovernanceRecord",
    "ModelProvider",
    "ModelRecord",
    "ModelStatus",
    "PipelineSpec",
    "PipelineStatus",
    "PredictionResult",
    "ReportFormat",
    "ReportGenerator",
    "ReportSpec",
    "SourceType",
    "build_engine",
    "coerce_bool",
    "coerce_number",
    "get_logger",
    "new_id",
    "numeric_values",
    "safe_get",
]
