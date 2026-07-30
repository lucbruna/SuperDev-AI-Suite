from __future__ import annotations

import time
import uuid
from typing import Any

from .database_interfaces import IDatabaseDriver, IConnectionPool, ITransactionManager
from .database_logger import DatabaseLogger
from .database_models import ConnectionConfig, QueryResult, TransactionInfo


class DatabaseContext:
    """Request-scoped database context wrapping a connection, transaction, and pool handle."""

    def __init__(
        self,
        driver: IDatabaseDriver,
        pool: IConnectionPool | None = None,
        logger: DatabaseLogger | None = None,
    ) -> None:
        self._driver = driver
        self._pool = pool
        self._logger = logger or DatabaseLogger("database.context")
        self._context_id: str = uuid.uuid4().hex
        self._created_at: float = time.time()
        self._transaction: TransactionInfo | None = None

    @property
    def context_id(self) -> str:
        return self._context_id

    @property
    def driver(self) -> IDatabaseDriver:
        return self._driver

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        return await self._driver.execute(query, params)

    async def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        return await self._driver.execute_query(query, params)

    async def begin(self) -> None:
        await self._driver.begin()
        self._transaction = TransactionInfo()

    async def commit(self) -> None:
        await self._driver.commit()
        self._transaction = None

    async def rollback(self) -> None:
        await self._driver.rollback()
        self._transaction = None

    @property
    def in_transaction(self) -> bool:
        return self._transaction is not None

    async def release(self) -> None:
        if self._pool:
            await self._pool.release(self._driver)

    async def ping(self) -> bool:
        return await self._driver.ping()

    def elapsed(self) -> float:
        return time.time() - self._created_at
