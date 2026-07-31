from __future__ import annotations

from typing import Any

from .memory_cache import MemoryCache
from .memory_checkpoint import MemoryCheckpoint
from .memory_config import MemoryConfig
from .memory_events import MemoryEvents
from .memory_logger import MemoryLogger
from .memory_metrics import MemoryMetrics
from .memory_optimizer import MemoryOptimizer
from .memory_permissions import MemoryPermissions
from .memory_profiler import MemoryProfiler
from .memory_scheduler import MemoryScheduler
from .memory_security import MemorySecurity
from .memory_statistics import MemoryStatistics
from .memory_validator import MemoryValidator


class MemoryFactory:
    """Factory for creating configured memory components."""

    def __init__(self, config: MemoryConfig | None = None):
        self._config = config or MemoryConfig.defaults()

    @property
    def config(self) -> MemoryConfig:
        return self._config

    def create_cache(self) -> MemoryCache:
        return MemoryCache(
            max_size=self._config.cache_max_size,
            default_ttl=self._config.cache_ttl,
        )

    def create_metrics(self) -> MemoryMetrics:
        return MemoryMetrics()

    def create_logger(self) -> MemoryLogger:
        return MemoryLogger()

    def create_events(self) -> MemoryEvents:
        return MemoryEvents()

    def create_validator(self) -> MemoryValidator:
        return MemoryValidator()

    def create_optimizer(self) -> MemoryOptimizer:
        return MemoryOptimizer(strategy=self._config.consolidation_strategy)

    def create_scheduler(self) -> MemoryScheduler:
        return MemoryScheduler()

    def create_checkpoint(self) -> MemoryCheckpoint:
        return MemoryCheckpoint()

    def create_security(self) -> MemorySecurity:
        return MemorySecurity(enable_audit=self._config.enable_audit)

    def create_permissions(self) -> MemoryPermissions:
        return MemoryPermissions()

    def create_profiler(self) -> MemoryProfiler:
        return MemoryProfiler()

    def create_statistics(self) -> MemoryStatistics:
        return MemoryStatistics()

    def create_all(self) -> dict[str, Any]:
        return {
            "cache": self.create_cache(),
            "metrics": self.create_metrics(),
            "logger": self.create_logger(),
            "events": self.create_events(),
            "validator": self.create_validator(),
            "optimizer": self.create_optimizer(),
            "scheduler": self.create_scheduler(),
            "checkpoint": self.create_checkpoint(),
            "security": self.create_security(),
            "permissions": self.create_permissions(),
            "profiler": self.create_profiler(),
            "statistics": self.create_statistics(),
        }
