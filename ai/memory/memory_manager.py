from __future__ import annotations

import time

from .memory_cache import MemoryCache
from .memory_config import MemoryConfig
from .memory_events import MemoryEvents
from .memory_logger import MemoryLogger
from .memory_metrics import MemoryMetrics
from .memory_models import MemoryEntry, MemoryQuery, MemorySummary
from .memory_optimizer import MemoryOptimizer
from .memory_permissions import MemoryAction, MemoryPermissions
from .memory_repository import MemoryRepository
from .memory_scheduler import MemoryScheduler
from .memory_security import MemorySecurity
from .memory_state import MemoryPhase, MemoryState
from .memory_statistics import MemoryStatistics
from .memory_types import (
    MemoryCategory,
    MemoryData,
    MemoryID,
    MemoryScope,
    MemoryStatus,
    Tags,
)
from .memory_validator import MemoryValidator


class MemoryManager:
    """Central manager for memory lifecycle, storage, and operations."""

    def __init__(
        self,
        config: MemoryConfig | None = None,
        repository: MemoryRepository | None = None,
        cache: MemoryCache | None = None,
        validator: MemoryValidator | None = None,
        optimizer: MemoryOptimizer | None = None,
        events: MemoryEvents | None = None,
        metrics: MemoryMetrics | None = None,
        logger: MemoryLogger | None = None,
        security: MemorySecurity | None = None,
        permissions: MemoryPermissions | None = None,
        scheduler: MemoryScheduler | None = None,
        statistics: MemoryStatistics | None = None,
    ):
        self._config = config or MemoryConfig.defaults()
        self._repository = repository or MemoryRepository()
        self._cache = cache or MemoryCache(self._config.cache_max_size, self._config.cache_ttl)
        self._validator = validator or MemoryValidator()
        self._optimizer = optimizer or MemoryOptimizer(self._config.consolidation_strategy)
        self._events = events or MemoryEvents()
        self._metrics = metrics or MemoryMetrics()
        self._logger = logger or MemoryLogger()
        self._security = security or MemorySecurity(enable_audit=self._config.enable_audit)
        self._permissions = permissions or MemoryPermissions()
        self._scheduler = scheduler or MemoryScheduler()
        self._statistics = statistics or MemoryStatistics()
        self._state = MemoryState()

    @property
    def config(self) -> MemoryConfig:
        return self._config

    @property
    def state(self) -> MemoryState:
        return self._state

    @property
    def metrics(self) -> MemoryMetrics:
        return self._metrics

    @property
    def events(self) -> MemoryEvents:
        return self._events

    @property
    def statistics(self) -> MemoryStatistics:
        return self._statistics

    @property
    def permissions(self) -> MemoryPermissions:
        return self._permissions

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
        if not self._permissions.can(user, MemoryAction.WRITE):
            self._logger.warn("Write permission denied", "store", key, {"user": user})
            return False
        start = time.time()
        entry = MemoryEntry(
            key=key,
            data=data,
            scope=scope or self._config.default_scope,
            category=category,
            tags=tags,
            ttl=ttl or self._config.default_ttl,
            priority=priority,
        )
        if not self._validator.validate_entry(entry):
            self._logger.error("Validation failed", "store", key, {"errors": self._validator.errors})
            self._metrics.record_error()
            return False
        await self._repository.store(entry)
        await self._cache.set(key, data, ttl or self._config.cache_ttl)
        self._metrics.record_store(time.time() - start)
        self._statistics.record_entry(entry)
        self._logger.info("Stored", "store", key, {"scope": scope.name if scope else "default"})
        await self._events.publish("STORED", {"key": key, "scope": scope.name if scope else None})
        self._security.audit("store", key, user)
        return True

    async def retrieve(
        self,
        key: MemoryID,
        user: str = "",
    ) -> MemoryData | None:
        if not self._permissions.can(user, MemoryAction.READ):
            self._logger.warn("Read permission denied", "retrieve", key, {"user": user})
            return None
        start = time.time()
        cached = await self._cache.get(key)
        if cached is not None:
            self._metrics.record_retrieve(True, time.time() - start)
            self._statistics.record_access(key)
            return cached
        entry = await self._repository.retrieve(key)
        if entry is None:
            self._metrics.record_retrieve(False, time.time() - start)
            return None
        await self._cache.set(key, entry.data)
        self._metrics.record_retrieve(True, time.time() - start)
        self._statistics.record_access(key)
        self._logger.info("Retrieved", "retrieve", key)
        await self._events.publish("RETRIEVED", {"key": key})
        self._security.audit("retrieve", key, user)
        return entry.data

    async def update(
        self,
        key: MemoryID,
        data: MemoryData,
        user: str = "",
    ) -> bool:
        if not self._permissions.can(user, MemoryAction.UPDATE):
            self._logger.warn("Update permission denied", "update", key, {"user": user})
            return False
        start = time.time()
        result = await self._repository.update(key, data)
        if result:
            await self._cache.set(key, data)
            self._metrics.record_update(time.time() - start)
            self._logger.info("Updated", "update", key)
            await self._events.publish("UPDATED", {"key": key})
            self._security.audit("update", key, user)
        return result

    async def delete(
        self,
        key: MemoryID,
        user: str = "",
    ) -> bool:
        if not self._permissions.can(user, MemoryAction.DELETE):
            self._logger.warn("Delete permission denied", "delete", key, {"user": user})
            return False
        start = time.time()
        result = await self._repository.delete(key)
        if result:
            await self._cache.delete(key)
            self._metrics.record_delete(time.time() - start)
            self._logger.info("Deleted", "delete", key)
            await self._events.publish("DELETED", {"key": key})
            self._security.audit("delete", key, user)
        return result

    async def search(self, query: MemoryQuery, user: str = "") -> list[MemoryEntry]:
        if not self._permissions.can(user, MemoryAction.READ):
            return []
        return await self._repository.search(query)

    async def consolidate(self) -> int:
        self._state.transition_to(MemoryPhase.CONSOLIDATING)
        entries = await self._repository.search(MemoryQuery(include_expired=True))
        optimized = self._optimizer.consolidate(entries)
        await self._repository.clear()
        count = 0
        for entry in optimized:
            await self._repository.store(entry)
            count += 1
        self._state.record_consolidation()
        if self._state.phase == MemoryPhase.CONSOLIDATING:
            self._state.transition_to(MemoryPhase.READY)
        self._logger.info("Consolidation complete", "consolidate", "", {"count": count})
        await self._events.publish("CONSOLIDATED", {"count": count})
        return count

    async def get_stats(self) -> MemorySummary:
        entries = await self._repository.search(MemoryQuery(include_expired=True))
        total_size = sum(e.size_bytes for e in entries)
        active = sum(1 for e in entries if e.status == MemoryStatus.ACTIVE)
        expired = sum(1 for e in entries if e.is_expired)
        by_scope: dict[str, int] = {}
        for e in entries:
            by_scope[e.scope.name] = by_scope.get(e.scope.name, 0) + 1
        by_category: dict[str, int] = {}
        for e in entries:
            by_category[e.category.name] = by_category.get(e.category.name, 0) + 1
        return MemorySummary(
            total_entries=len(entries),
            total_size_bytes=total_size,
            active_entries=active,
            expired_entries=expired,
            by_scope=by_scope,
            by_category=by_category,
        )

    async def clear(self, scope: MemoryScope | None = None) -> None:
        await self._repository.clear(scope)
        if scope is None:
            await self._cache.clear()

    async def evict_expired(self) -> int:
        entries = await self._repository.search(MemoryQuery(include_expired=True, status=MemoryStatus.ACTIVE))
        expired = [e for e in entries if e.is_expired]
        count = 0
        for entry in expired:
            if await self._repository.delete(entry.key):
                await self._cache.delete(entry.key)
                count += 1
        if count:
            self._metrics.record_eviction()
        return count
