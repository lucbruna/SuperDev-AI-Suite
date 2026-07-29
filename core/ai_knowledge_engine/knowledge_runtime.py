from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .knowledge_config import KnowledgeConfig
from .knowledge_context import KnowledgeContext
from .knowledge_events import KnowledgeEventBus, KnowledgeEvent, EventType
from .knowledge_metrics import KnowledgeMetrics, MetricsCollector
from .knowledge_security import KnowledgeSecurityManager
from .knowledge_logger import KnowledgeLogger, LogLevel
from .knowledge_registry import KnowledgeRegistry

logger = logging.getLogger(__name__)


class RuntimeState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class RuntimeStats:
    state: RuntimeState = RuntimeState.STOPPED
    uptime_seconds: float = 0.0
    active_subsystems: int = 0
    total_subsystems: int = 0
    events_processed: int = 0
    memory_entries: int = 0
    last_heartbeat: Optional[datetime] = None
    start_time: Optional[datetime] = None


class KnowledgeRuntime:
    def __init__(self, config: KnowledgeConfig, event_bus: KnowledgeEventBus,
                 context: KnowledgeContext, security: KnowledgeSecurityManager,
                 registry: KnowledgeRegistry, logger: KnowledgeLogger):
        self.config = config
        self.event_bus = event_bus
        self.context = context
        self.security = security
        self.registry = registry
        self.logger = logger
        self.stats = RuntimeStats()
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self._running:
            return
        self.stats.state = RuntimeState.STARTING
        self.stats.start_time = datetime.utcnow()
        await self.event_bus.start_processor()
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.stats.state = RuntimeState.RUNNING
        self.logger.info("runtime", "Knowledge Runtime started")
        await self.event_bus.publish(KnowledgeEvent(
            event_type=EventType.KNOWLEDGE_SYNCED,
            payload={"action": "runtime_started"},
            source="runtime",
        ))

    async def stop(self) -> None:
        self.stats.state = RuntimeState.STOPPING
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        await self.event_bus.stop_processor()
        self.stats.state = RuntimeState.STOPPED
        self.logger.info("runtime", "Knowledge Runtime stopped")

    async def pause(self) -> None:
        self._running = False
        self.stats.state = RuntimeState.PAUSED
        self.logger.info("runtime", "Knowledge Runtime paused")

    async def resume(self) -> None:
        if self.stats.state == RuntimeState.PAUSED:
            self._running = True
            self.stats.state = RuntimeState.RUNNING
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self.logger.info("runtime", "Knowledge Runtime resumed")

    def get_status(self) -> Dict[str, Any]:
        uptime = 0.0
        if self.stats.start_time and self.stats.state == RuntimeState.RUNNING:
            uptime = (datetime.utcnow() - self.stats.start_time).total_seconds()
        return {
            "state": self.stats.state.value,
            "uptime_seconds": uptime,
            "active_subsystems": len(self._subsystems),
            "events_processed": sum(self.event_bus._event_counts.values()) if hasattr(self.event_bus, '_event_counts') else 0,
            "last_heartbeat": self.stats.last_heartbeat.isoformat() if self.stats.last_heartbeat else None,
        }

    def is_running(self) -> bool:
        return self._running and self.stats.state == RuntimeState.RUNNING

    def get_runtime_stats(self) -> RuntimeStats:
        if self.stats.start_time:
            self.stats.uptime_seconds = (datetime.utcnow() - self.stats.start_time).total_seconds()
        self.stats.active_subsystems = len(self._subsystems)
        self.stats.total_subsystems = self.registry.count()
        return self.stats

    def register_subsystem(self, name: str, subsystem: Any) -> None:
        self._subsystems[name] = subsystem
        self.registry.register(name, subsystem, "subsystem", "runtime")

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)

    async def _heartbeat_loop(self) -> None:
        while self._running:
            self.stats.last_heartbeat = datetime.utcnow()
            await asyncio.sleep(30)