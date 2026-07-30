from __future__ import annotations

from typing import Any

from .monitoring_config import MonitoringConfig
from .monitoring_engine import MonitoringEngine
from .monitoring_registry import MonitoringRegistry


class MonitoringManager:
    """High-level lifecycle manager for the monitoring platform."""

    def __init__(self, config: MonitoringConfig | None = None) -> None:
        self._config = config or MonitoringConfig.default()
        self._engine: MonitoringEngine | None = None
        self._registry = MonitoringRegistry()

    async def initialize(self) -> MonitoringEngine:
        engine = MonitoringEngine(config=self._config)
        await engine.start()
        self._engine = engine
        return engine

    async def shutdown(self) -> None:
        if self._engine:
            await self._engine.stop()

    async def reload(self) -> None:
        await self.shutdown()
        await self.initialize()

    def get_engine(self) -> MonitoringEngine:
        if self._engine is None:
            raise RuntimeError("Engine not initialized")
        return self._engine

    @property
    def registry(self) -> MonitoringRegistry:
        return self._registry

    @property
    def config(self) -> MonitoringConfig:
        return self._config


__all__ = ["MonitoringManager"]
