"""Configuration for the Data Intelligence & Analytics Engine."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass
class DataIntelligenceConfig:
    """Runtime configuration for the engine.

    Attributes mirror the knobs used across the subsystems; every field
    has a sensible default so ``build_engine()`` works out of the box.
    """

    engine_name: str = "data_intelligence"
    enabled: bool = True
    max_batch_size: int = 1000
    default_format: str = "json"
    timezone: str = "UTC"
    locale: str = "pt_BR"
    pipeline_timeout: float = 120.0
    ml_seed: int = 42
    retention_days: int = 90
    lake_zone_prefix: str = "raw"
    warehouse_schema: str = "analytics"
    log_level: str = "INFO"
    extra: dict[str, Any] = field(default_factory=dict)

    def merge(self, **overrides: Any) -> "DataIntelligenceConfig":
        """Returns a copy with the given fields replaced."""
        return replace(self, **overrides)
