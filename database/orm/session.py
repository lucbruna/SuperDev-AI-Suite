from __future__ import annotations

from typing import Any

from ..database_interfaces import IDatabaseDriver
from ..database_models import QueryResult
from .model import Model
from .query_builder import QueryBuilder


class Session:
    """Unit-of-work session that tracks model changes and flushes them to the
    database through a driver.

    Typical lifecycle::

        session = Session(driver)
        user = User(name="Alice")
        await session.add(user)
        await session.commit()
        await session.close()
    """

    def __init__(self, driver: IDatabaseDriver) -> None:
        self._driver = driver
        self._new: list[Model] = []
        self._dirty: list[Model] = []
        self._deleted: list[Model] = []
        self._closed = False

    # -- lifecycle ------------------------------------------------------------

    async def add(self, model: Model) -> None:
        self._new.append(model)

    async def delete(self, model: Model) -> None:
        self._deleted.append(model)

    async def flush(self) -> list[QueryResult]:
        results: list[QueryResult] = []
        for model in self._new:
            results.append(await self._insert(model))
        self._new.clear()
        for model in self._dirty:
            results.append(await self._update(model))
        self._dirty.clear()
        for model in self._deleted:
            results.append(await self._delete(model))
        self._deleted.clear()
        return results

    async def commit(self) -> list[QueryResult]:
        return await self.flush()

    async def rollback(self) -> None:
        self._new.clear()
        self._dirty.clear()
        self._deleted.clear()

    async def close(self) -> None:
        self._closed = True

    # -- accessors ------------------------------------------------------------

    def get_driver(self) -> IDatabaseDriver:
        return self._driver

    @property
    def is_open(self) -> bool:
        return not self._closed

    # -- internal helpers -----------------------------------------------------

    async def _insert(self, model: Model) -> QueryResult:
        qb = QueryBuilder(dialect=self._driver.dialect)
        values = model.to_dict()
        pk = model.pk_name()
        if pk and values.get(pk) is None and self._driver.dialect == "postgresql":
            qb.returning("*")
        qb.insert(model._table).set_values(values)
        sql, params = qb.build()
        return await self._driver.execute(sql, params)

    async def _update(self, model: Model) -> QueryResult:
        qb = QueryBuilder(dialect=self._driver.dialect)
        pk = model.pk_name()
        pk_value = model.pk_value()
        values = model.to_dict()
        if pk and pk in values:
            del values[pk]
        qb.update(model._table).set_values(values)
        if pk and pk_value is not None:
            qb.where(f"{qb._quote(pk)} = {qb._ph()}", pk_value)
        sql, params = qb.build()
        return await self._driver.execute(sql, params)

    async def _delete(self, model: Model) -> QueryResult:
        qb = QueryBuilder(dialect=self._driver.dialect)
        pk = model.pk_name()
        pk_value = model.pk_value()
        qb.delete(model._table)
        if pk and pk_value is not None:
            qb.where(f"{qb._quote(pk)} = {qb._ph()}", pk_value)
        sql, params = qb.build()
        return await self._driver.execute(sql, params)


__all__ = [
    "Session",
]
