from __future__ import annotations

from typing import Any

from ..database_interfaces import IDatabaseDriver, ITransactionManager
from ..database_models import IsolationLevel, TransactionInfo


class TransactionManager(ITransactionManager):
    """Manages database transactions for a given driver."""

    def __init__(self, driver: IDatabaseDriver) -> None:
        self._driver = driver
        self._current: TransactionInfo | None = None

    async def begin(self) -> TransactionInfo:
        if self._current is not None:
            raise RuntimeError("Transaction already in progress")
        await self._driver.begin()
        self._current = TransactionInfo()
        return self._current

    async def commit(self) -> None:
        if self._current is None:
            raise RuntimeError("No active transaction")
        await self._driver.commit()
        self._current.is_active = False
        self._current = None

    async def rollback(self) -> None:
        if self._current is None:
            raise RuntimeError("No active transaction")
        await self._driver.rollback()
        self._current.is_active = False
        self._current = None

    async def savepoint(self, name: str) -> None:
        if self._current is None:
            raise RuntimeError("No active transaction")
        self._current.savepoints.append(name)

    async def rollback_to_savepoint(self, name: str) -> None:
        if self._current is None:
            raise RuntimeError("No active transaction")
        if name not in self._current.savepoints:
            raise ValueError(f"Savepoint {name!r} not found")
        self._current.savepoints = [s for s in self._current.savepoints if s != name]

    async def release_savepoint(self, name: str) -> None:
        if self._current is None:
            raise RuntimeError("No active transaction")
        self._current.savepoints = [s for s in self._current.savepoints if s != name]

    @property
    def in_transaction(self) -> bool:
        return self._current is not None


__all__ = [
    "TransactionManager",
]
