"""Analytics configuration."""
from dataclasses import dataclass, field


@dataclass
class AnalyticsConfig:
    enabled: bool = True
    warehouse_type: str = "memory"
    warehouse_url: str = ""
    cache_ttl: int = 300
    batch_size: int = 1000
    max_concurrent_queries: int = 10
    insight_confidence_threshold: float = 0.7
    retention_days: int = 90
    export_formats: list[str] = field(default_factory=lambda: ["json", "csv"])
    custom_dimensions: dict[str, str] = field(default_factory=dict)


@dataclass
class DashboardConfig:
    refresh_interval: int = 60
    max_widgets: int = 20
    theme: str = "light"
    auto_refresh: bool = True
    allow_export: bool = True


@dataclass
class ReportConfig:
    output_dir: str = "./reports"
    default_format: str = "html"
    include_charts: bool = True
    max_rows: int = 10000
