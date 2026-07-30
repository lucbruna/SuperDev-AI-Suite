from __future__ import annotations

import asyncio
from typing import Any

from .monitoring_config import MonitoringConfig
from .monitoring_events import MonitoringEventBus
from .monitoring_logger import MonitoringLogger
from .monitoring_metrics import MonitoringMetrics
from .monitoring_repository import MonitoringRepository


class MonitoringEngine:
    """Central orchestrator for the monitoring & observability platform."""

    def __init__(
        self,
        config: MonitoringConfig | None = None,
    ) -> None:
        self._config = config or MonitoringConfig.default()
        self._event_bus = MonitoringEventBus()
        self._logger = MonitoringLogger(name="monitoring-engine")
        self._metrics = MonitoringMetrics()
        self._repository = MonitoringRepository()
        self._running = False
        self._tasks: list[asyncio.Task[Any]] = []

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        self._running = True
        await self._event_bus.emit("engine.started", {"config": self._config})
        self._logger.info("MonitoringEngine started")

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks:
            task.cancel()
        await self._event_bus.emit("engine.stopped", {})
        self._logger.info("MonitoringEngine stopped")

    async def health(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "metrics_count": len(self._metrics.get_snapshot()),
            "config": {
                "metrics": self._config.metrics_enabled,
                "logs": self._config.logs_enabled,
                "tracing": self._config.tracing_enabled,
                "alerts": self._config.alerts_enabled,
            },
        }

    # -- accessors -----------------------------------------------------------

    @property
    def config(self) -> MonitoringConfig:
        return self._config

    @property
    def event_bus(self) -> MonitoringEventBus:
        return self._event_bus

    @property
    def logger(self) -> MonitoringLogger:
        return self._logger

    @property
    def metrics(self) -> MonitoringMetrics:
        return self._metrics

    @property
    def repository(self) -> MonitoringRepository:
        return self._repository

    @property
    def is_running(self) -> bool:
        return self._running


__all__ = ["MonitoringEngine"]
