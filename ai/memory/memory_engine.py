from __future__ import annotations

from typing import Any, Dict, List, Optional

from .memory_cache import MemoryCache
from .memory_config import MemoryConfig
from .memory_events import MemoryEvents
from .memory_factory import MemoryFactory
from .memory_logger import MemoryLogger
from .memory_manager import MemoryManager
from .memory_metrics import MemoryMetrics
from .memory_models import MemoryEntry, MemorySummary
from .memory_repository import MemoryRepository
from .memory_runtime import MemoryRuntime
from .memory_scheduler import MemoryScheduler
from .memory_service import MemoryService
from .memory_state import MemoryState
from .memory_types import MemoryCategory, MemoryData, MemoryID, MemoryScope, Tags


class MemoryEngine:
    """Core memory engine orchestrating all memory operations."""

    def __init__(
        self,
        config: MemoryConfig | None = None,
        factory: MemoryFactory | None = None,
    ):
        self._config = config or MemoryConfig.defaults()
        self._factory = factory or MemoryFactory(self._config)
        self._runtime = MemoryRuntime()
        self._repository = MemoryRepository()
        self._cache = self._factory.create_cache()
        self._metrics = self._factory.create_metrics()
        self._logger = self._factory.create_logger()
        self._events = self._factory.create_events()
        self._scheduler = self._factory.create_scheduler()
        self._manager = MemoryManager(
            config=self._config,
            repository=self._repository,
            cache=self._cache,
            validator=self._factory.create_validator(),
            optimizer=self._factory.create_optimizer(),
            events=self._events,
            metrics=self._metrics,
            logger=self._logger,
            security=self._factory.create_security(),
            permissions=self._factory.create_permissions(),
            scheduler=self._scheduler,
            statistics=self._factory.create_statistics(),
        )
        self._service = MemoryService(self._manager)

    @property
    def config(self) -> MemoryConfig:
        return self._config

    @property
    def manager(self) -> MemoryManager:
        return self._manager

    @property
    def service(self) -> MemoryService:
        return self._service

    @property
    def runtime(self) -> MemoryRuntime:
        return self._runtime

    @property
    def events(self) -> MemoryEvents:
        return self._events

    @property
    def metrics(self) -> MemoryMetrics:
        return self._metrics

    @property
    def state(self) -> MemoryState:
        return self._manager.state

    def start(self) -> None:
        self._runtime.start()
        self._logger.info("Memory engine started", "start")

    def shutdown(self) -> None:
        self._scheduler.stop()
        self._runtime.shutdown()
        self._logger.info("Memory engine shut down", "shutdown")

    async def store(
        self,
        key: MemoryID,
        data: MemoryData,
        scope: MemoryScope | None = None,
        category: MemoryCategory = MemoryCategory.CONTEXT,
        tags: Tags | None = None,
        ttl: float | None = None,
        priority: int = 0,
        user: str = "",
    ) -> bool:
        self._runtime.before_store()
        result = await self._manager.store(key, data, scope, category, tags, ttl, priority, user)
        self._runtime.after_store()
        return result

    async def retrieve(self, key: MemoryID, user: str = "") -> MemoryData | None:
        self._runtime.before_retrieve()
        result = await self._manager.retrieve(key, user)
        self._runtime.after_retrieve()
        return result

    async def update(self, key: MemoryID, data: MemoryData, user: str = "") -> bool:
        return await self._manager.update(key, data, user)

    async def delete(self, key: MemoryID, user: str = "") -> bool:
        return await self._manager.delete(key, user)

    async def search(self, query: str, user: str = "") -> List[MemoryEntry]:
        return await self._service.find(query, user)

    async def remember(self, key: MemoryID, data: MemoryData, user: str = "") -> bool:
        return await self._service.remember(key, data, user=user)

    async def recall(self, key: MemoryID, user: str = "") -> MemoryData | None:
        return await self._service.recall(key, user)

    async def forget(self, key: MemoryID, user: str = "") -> bool:
        return await self._service.forget(key, user)

    async def get_stats(self) -> MemorySummary:
        return await self._manager.get_stats()

    async def get_metrics_snapshot(self) -> Dict[str, Any]:
        return self._metrics.snapshot()

    async def run_maintenance(self) -> Dict[str, Any]:
        return await self._service.run_maintenance()
