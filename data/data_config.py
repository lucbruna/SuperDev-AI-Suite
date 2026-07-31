from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IngestionConfig:
    enabled: bool = True
    batch_size: int = 1000
    max_retries: int = 3
    backoff_s: float = 1.0
    timeout_s: float = 30.0


@dataclass
class ProcessingConfig:
    enabled: bool = True
    auto_clean: bool = True
    auto_normalize: bool = True
    deduplicate: bool = True
    anonymize_pii: bool = True


@dataclass
class PipelineConfig:
    enabled: bool = True
    max_concurrent_runs: int = 4
    retry_on_failure: bool = True
    max_retries: int = 2
    checkpoint_enabled: bool = True


@dataclass
class WarehouseConfig:
    enabled: bool = True
    database_url: str = "sqlite:///data_warehouse.db"
    partitioning_enabled: bool = True
    optimization_enabled: bool = True


@dataclass
class LakeConfig:
    enabled: bool = True
    root_path: str = "data/lake"
    zones: list[str] = field(default_factory=lambda: ["raw", "processed", "curated"])
    lifecycle_enabled: bool = True


@dataclass
class EtlConfig:
    enabled: bool = True
    scheduler_enabled: bool = True
    validation_enabled: bool = True
    monitoring_enabled: bool = True


@dataclass
class AnalyticsConfig:
    enabled: bool = True
    correlation_enabled: bool = True
    segmentation_enabled: bool = True
    pattern_detection_enabled: bool = True


@dataclass
class BIConfig:
    enabled: bool = True
    dashboards_enabled: bool = True
    kpi_tracking_enabled: bool = True
    report_builder_enabled: bool = True


@dataclass
class MLConfig:
    enabled: bool = True
    training_enabled: bool = True
    deployment_enabled: bool = True
    experiment_tracking_enabled: bool = True
    default_algorithm: str = "linear_regression"


@dataclass
class ForecastingConfig:
    enabled: bool = True
    default_horizon: int = 30
    default_method: str = "moving_average"
    anomaly_threshold: float = 2.5


@dataclass
class ReportingConfig:
    enabled: bool = True
    default_format: str = "markdown"
    export_path: str = "data/reports"
    scheduling_enabled: bool = True


@dataclass
class VisualizationConfig:
    enabled: bool = True
    realtime_enabled: bool = True
    interactive_enabled: bool = True
    max_data_points: int = 10000


@dataclass
class GovernanceConfig:
    enabled: bool = True
    compliance_enabled: bool = True
    privacy_enabled: bool = True
    retention_enabled: bool = True
    default_retention_days: int = 90


@dataclass
class QualityConfig:
    enabled: bool = True
    completeness_threshold: float = 0.9
    accuracy_threshold: float = 0.95
    profiling_enabled: bool = True
    monitoring_enabled: bool = True


@dataclass
class CatalogConfig:
    enabled: bool = True
    discovery_enabled: bool = True
    lineage_tracking_enabled: bool = True
    classification_enabled: bool = True


@dataclass
class StreamingConfig:
    enabled: bool = True
    buffer_size: int = 10000
    window_seconds: int = 60
    realtime_analysis_enabled: bool = True


@dataclass
class DataConfig:
    """Top-level configuration for the Data & Analytics Engine."""

    environment: str = "development"
    debug: bool = False
    realtime_enabled: bool = True

    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    pipelines: PipelineConfig = field(default_factory=PipelineConfig)
    warehouse: WarehouseConfig = field(default_factory=WarehouseConfig)
    lake: LakeConfig = field(default_factory=LakeConfig)
    etl: EtlConfig = field(default_factory=EtlConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    bi: BIConfig = field(default_factory=BIConfig)
    machine_learning: MLConfig = field(default_factory=MLConfig)
    forecasting: ForecastingConfig = field(default_factory=ForecastingConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    catalog: CatalogConfig = field(default_factory=CatalogConfig)
    streaming: StreamingConfig = field(default_factory=StreamingConfig)

    @classmethod
    def default(cls) -> DataConfig:
        return cls()

    @classmethod
    def from_env(cls) -> DataConfig:
        config = cls()
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.warehouse.database_url = os.getenv(
            "DATA_WAREHOUSE_URL", config.warehouse.database_url
        )
        config.lake.root_path = os.getenv("DATA_LAKE_PATH", config.lake.root_path)
        return config


__all__ = [
    "IngestionConfig", "ProcessingConfig", "PipelineConfig",
    "WarehouseConfig", "LakeConfig", "EtlConfig", "AnalyticsConfig",
    "BIConfig", "MLConfig", "ForecastingConfig", "ReportingConfig",
    "VisualizationConfig", "GovernanceConfig", "QualityConfig",
    "CatalogConfig", "StreamingConfig", "DataConfig",
]
