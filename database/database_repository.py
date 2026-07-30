from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from .database_interfaces import IDatabaseDriver, IRepository
from .database_logger import DatabaseLogger

T = TypeVar("T")


class DatabaseRepository(IRepository, ABC, Generic[T]):
    """Base repository providing CRUD operations with optional caching."""

    def __init__(
        self,
        driver: IDatabaseDriver,
        table: str = "",
        logger: DatabaseLogger | None = None,
    ) -> None:
        self._driver = driver
        self._table = table
        self._logger = logger or DatabaseLogger(f"repository.{table}" if table else "repository")

    @property
    def table(self) -> str:
        return self._table

    @property
    def driver(self) -> IDatabaseDriver:
        return self._driver

    async def get(self, id: Any) -> T | None:
        query = f'SELECT * FROM "{self._table}" WHERE id = ?'
        result = await self._driver.execute_query(query, [id])
        if not result:
            return None
        return self._to_entity(result[0])  # type: ignore[return-value]

    async def list(self, filters: dict[str, Any] | None = None) -> list[T]:
        if not filters:
            query = f'SELECT * FROM "{self._table}"'
            result = await self._driver.execute_query(query)
        else:
            conditions = [f'"{k}" = ?' for k in filters]
            query = f'SELECT * FROM "{self._table}" WHERE {" AND ".join(conditions)}'
            result = await self._driver.execute_query(query, list(filters.values()))
        return [self._to_entity(row) for row in result]  # type: ignore[misc]

    async def create(self, entity: T) -> T:
        data = self._from_entity(entity)
        columns = [f'"{k}"' for k in data]
        placeholders = ["?" for _ in data]
        query = f'INSERT INTO "{self._table}" ({", ".join(columns)}) VALUES ({", ".join(placeholders)})'
        await self._driver.execute(query, list(data.values()))
        return entity

    async def update(self, entity: T) -> T:
        data = self._from_entity(entity)
        if "id" not in data:
            raise ValueError("Entity must have an 'id' field for update")
        entity_id = data.pop("id")
        set_clause = ", ".join(f'"{k}" = ?' for k in data)
        query = f'UPDATE "{self._table}" SET {set_clause} WHERE id = ?'
        await self._driver.execute(query, list(data.values()) + [entity_id])
        data["id"] = entity_id
        return entity

    async def delete(self, id: Any) -> bool:
        query = f'DELETE FROM "{self._table}" WHERE id = ?'
        result = await self._driver.execute(query, [id])
        return result.row_count > 0

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        if not filters:
            query = f'SELECT COUNT(*) as cnt FROM "{self._table}"'
            result = await self._driver.execute_query(query)
        else:
            conditions = [f'"{k}" = ?' for k in filters]
            query = f'SELECT COUNT(*) as cnt FROM "{self._table}" WHERE {" AND ".join(conditions)}'
            result = await self._driver.execute_query(query, list(filters.values()))
        return result[0]["cnt"] if result else 0

    @abstractmethod
    def _to_entity(self, row: dict[str, Any]) -> T:
        ...

    def _from_entity(self, entity: T) -> dict[str, Any]:
        if hasattr(entity, "to_dict"):
            return entity.to_dict()  # type: ignore[return-value]
        if isinstance(entity, dict):
            return entity
        return entity.__dict__  # type: ignore[return-value]
