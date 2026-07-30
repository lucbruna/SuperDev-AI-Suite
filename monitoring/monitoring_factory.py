from __future__ import annotations

from typing import Any

from .monitoring_config import MonitoringConfig
from .monitoring_engine import MonitoringEngine
from .monitoring_manager import MonitoringManager


class MonitoringFactory:
    """Factory for creating monitoring components from config."""

    @staticmethod
    def create_engine(config: MonitoringConfig | None = None) -> MonitoringEngine:
        return MonitoringEngine(config=config or MonitoringConfig.default())

    @staticmethod
    def create_manager(config: MonitoringConfig | None = None) -> MonitoringManager:
        return MonitoringManager(config=config or MonitoringConfig.default())

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MonitoringConfig:
        return MonitoringConfig(**{
            k: v for k, v in data.items()
            if k in MonitoringConfig.__dataclass_fields__
        })


__all__ = ["MonitoringFactory"]
