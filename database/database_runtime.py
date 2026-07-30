from __future__ import annotations

import asyncio
from typing import Any

from .database_context import DatabaseContext
from .database_engine import DatabaseEngine
from .database_logger import DatabaseLogger
from .database_registry import DatabaseRegistry


class DatabaseRuntime:
    """Async runtime for connection management, pool handling, and execution."""

    def __init__(
        self,
        engine: DatabaseEngine,
        registry: DatabaseRegistry,
        logger: DatabaseLogger | None = None,
    ) -> None:
        self._engine = engine
        self._registry = registry
        self._logger = logger or DatabaseLogger("database.runtime")
        self._contexts: dict[str, DatabaseContext] = {}
        self._lock = asyncio.Lock()

    async def acquire_context(self, driver_name: str | None = None) -> DatabaseContext:
        name = driver_name or self._engine.config.default_driver
        driver = self._registry.get_driver(name)
        conn_cfg = self._registry.get_connection(name)

        if conn_cfg and not driver.is_connected:
            await driver.connect(conn_cfg)

        ctx = DatabaseContext(driver=driver, logger=self._logger)
        async with self._lock:
            self._contexts[ctx.context_id] = ctx
        return ctx

    async def release_context(self, ctx: DatabaseContext) -> None:
        if ctx.in_transaction:
            await ctx.rollback()
        await ctx.release()
        async with self._lock:
            self._contexts.pop(ctx.context_id, None)

    async def execute_in_context(
        self,
        query: str,
        params: list[Any] | None = None,
        driver_name: str | None = None,
    ) -> Any:
        ctx = await self.acquire_context(driver_name)
        try:
            return await ctx.execute(query, params)
        finally:
            await self.release_context(ctx)

    async def execute_query_in_context(
        self,
        query: str,
        params: list[Any] | None = None,
        driver_name: str | None = None,
    ) -> list[dict[str, Any]]:
        ctx = await self.acquire_context(driver_name)
        try:
            return await ctx.execute_query(query, params)
        finally:
            await self.release_context(ctx)

    def active_contexts(self) -> int:
        return len(self._contexts)

    def get_context_ids(self) -> list[str]:
        return list(self._contexts.keys())

    async def close_all(self) -> None:
        async with self._lock:
            for ctx_id, ctx in list(self._contexts.items()):
                try:
                    await ctx.release()
                except Exception as exc:
                    self._logger.error(f"Failed to release context {ctx_id}: {exc}")
            self._contexts.clear()
