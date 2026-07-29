from typing import Optional

from observability.core.configuration import ObservabilityConfig
from observability.logging.log_manager import LogManager
from observability.metrics.metrics_manager import MetricsManager
from observability.tracing.tracing_manager import TracingManager


class ObservabilityManager:
    _instance: Optional["ObservabilityManager"] = None
    _config: Optional[ObservabilityConfig] = None
    _log_manager: Optional[LogManager] = None
    _metrics_manager: Optional[MetricsManager] = None
    _tracing_manager: Optional[TracingManager] = None