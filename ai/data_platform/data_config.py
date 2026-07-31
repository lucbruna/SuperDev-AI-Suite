"""Data Platform Config — Configuration for the data platform."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class DataPlatformConfig:
    max_records_per_batch: int = 10000
    max_concurrent_pipelines: int = 10
    storage_tier_thresholds: Dict[str, int] = field(default_factory=lambda: {
        "hot_days": 30,
        "warm_days": 90,
        "cold_days": 365,
    })
    quality_threshold: float = 0.8
    retention_days: int = 730
    encryption_enabled: bool = True
    audit_logging: bool = True
    max_query_results: int = 100000
    streaming_batch_size: int = 100
    ml_training_split: float = 0.8
    enable_lineage_tracking: bool = True
