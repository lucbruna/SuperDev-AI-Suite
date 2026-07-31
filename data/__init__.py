"""Data & Analytics Engine — SuperDev AI Suite Volume 12.

Collect, organize, analyze and transform data produced by all SuperDev modules
into business intelligence: dashboards, ML models, forecasts, governance and
real-time analytics.
"""
from __future__ import annotations

from .data_config import DataConfig
from .data_context import DataContext
from .data_engine import DataEngine
from .data_events import DataEventBus
from .data_factory import DataFactory
from .data_logger import DataLogger
from .data_manager import DataManager
from .data_metrics import DataMetrics
from .data_models import (
    AnalyticsResult,
    AnomalyAlert,
    AnomalySeverity,
    ChartType,
    DataAsset,
    DataBatch,
    DataClassification,
    DataFormat,
    DataQualityReport,
    DataQualityStatus,
    DataRecord,
    DataSourceType,
    DataState,
    DashboardConfig,
    Dimension,
    EtlJob,
    EtlJobStatus,
    FactTable,
    ForecastResult,
    GovernancePolicy,
    IngestionResult,
    IngestionSource,
    KPI,
    LakeObject,
    MLModel,
    MetricDefinition,
    ModelStatus,
    ModelVersion,
    PipelineDefinition,
    PipelineRun,
    PipelineRunStatus,
    PipelineStatus,
    Report,
    ReportFormat,
    RetentionPolicy,
    StarSchema,
    StreamEvent,
    StreamWindow,
    TrainingRun,
)
from .data_registry import DataRegistry
from .data_runtime import DataRuntime
from .data_security import DataSecurity

from .ingestion.ingestion_engine import IngestionEngine
from .processing.processing_engine import ProcessingEngine
from .pipelines.pipeline_engine import PipelineEngine
from .warehouse.warehouse_engine import WarehouseEngine
from .lake.lake_engine import LakeEngine
from .etl.etl_engine import EtlEngine
from .analytics.analytics_engine import AnalyticsEngine
from .bi.bi_engine import BIEngine
from .machine_learning.ml_engine import MLEngine
from .forecasting.forecasting_engine import ForecastingEngine
from .reporting.report_engine import ReportEngine
from .visualization.visualization_engine import VisualizationEngine
from .governance.governance_engine import GovernanceEngine
from .quality.quality_engine import QualityEngine
from .catalog.catalog_engine import CatalogEngine
from .streaming.streaming_engine import StreamingEngine

__version__ = "1.0.0"
__all__ = [
    "DataConfig", "DataContext", "DataEngine", "DataEventBus", "DataFactory",
    "DataLogger", "DataManager", "DataMetrics", "DataRegistry", "DataRuntime",
    "DataSecurity",
    # Models
    "AnalyticsResult", "AnomalyAlert", "AnomalySeverity", "ChartType",
    "DataAsset", "DataBatch", "DataClassification", "DataFormat",
    "DataQualityReport", "DataQualityStatus", "DataRecord", "DataSourceType",
    "DataState", "DashboardConfig", "Dimension", "EtlJob", "EtlJobStatus",
    "FactTable", "ForecastResult", "GovernancePolicy", "IngestionResult",
    "IngestionSource", "KPI", "LakeObject", "MLModel", "MetricDefinition",
    "ModelStatus", "ModelVersion", "PipelineDefinition", "PipelineRun",
    "PipelineRunStatus", "PipelineStatus", "Report", "ReportFormat",
    "RetentionPolicy", "StarSchema", "StreamEvent", "StreamWindow",
    "TrainingRun",
    # Subsystem engines
    "IngestionEngine", "ProcessingEngine", "PipelineEngine", "WarehouseEngine",
    "LakeEngine", "EtlEngine", "AnalyticsEngine", "BIEngine", "MLEngine",
    "ForecastingEngine", "ReportEngine", "VisualizationEngine",
    "GovernanceEngine", "QualityEngine", "CatalogEngine", "StreamingEngine",
]
