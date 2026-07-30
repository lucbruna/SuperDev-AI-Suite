from __future__ import annotations

from typing import Any

from ..database_interfaces import IRepository
from ..database_models import QueryResult
from ..orm.model import Model
from ..orm.query_builder import QueryBuilder
from ..orm.session import Session


class BaseRepository(IRepository):
    """Abstract repository backed by a :class:`Session` and a :class:`Model`.

    Concrete subclasses must set ``_model_class``::

        class UserRepository(BaseRepository):
            _model_class = User
    """

    _model_class: type[Model]

    def __init__(self, session: Session) -> None:
        self._session = session
        self._driver = session.get_driver()
        self._qb = QueryBuilder(dialect=self._driver.dialect)

    async def get(self, id: Any) -> Model | None:
        pk = self._model_class._get_pk_name()
        if pk is None:
            raise ValueError(f"{self._model_class.__name__} has no primary key field")
        qb = QueryBuilder(dialect=self._driver.dialect)
        qb.select("*").from_table(self._model_class._table).where(
            f"{qb._quote(pk)} = {qb._ph()}", id
        )
        sql, params = qb.build()
        result = await self._driver.execute_query(sql, params)
        if not result:
            return None
        return self._model_class.from_dict(result[0])

    async def list(self, filters: dict[str, Any] | None = None) -> list[Model]:
        qb = QueryBuilder(dialect=self._driver.dialect)
        qb.select("*").from_table(self._model_class._table)
        if filters:
            for key, value in filters.items():
                qb.where(f"{qb._quote(key)} = {qb._ph()}", value)
        sql, params = qb.build()
        rows = await self._driver.execute_query(sql, params)
        return [self._model_class.from_dict(row) for row in rows]

    async def create(self, entity: Model) -> Model:
        await self._session.add(entity)
        await self._session.flush()
        return entity

    async def update(self, entity: Model) -> Model:
        pk = entity.pk_value()
        if pk is None:
            raise ValueError("Cannot update entity without a primary key value")
        old = await self.get(pk)
        if old is None:
            raise ValueError(f"Entity with pk={pk} not found")
        qb = QueryBuilder(dialect=self._driver.dialect)
        pk_name = entity.pk_name()
        if pk_name:
            values = entity.to_dict()
            del values[pk_name]
            qb.update(entity._table).set_values(values).where(
                f"{qb._quote(pk_name)} = {qb._ph()}", pk
            )
            sql, params = qb.build()
            await self._driver.execute(sql, params)
        return entity

    async def delete(self, id: Any) -> bool:
        pk = self._model_class._get_pk_name()
        if pk is None:
            raise ValueError(f"{self._model_class.__name__} has no primary key field")
        qb = QueryBuilder(dialect=self._driver.dialect)
        qb.delete(self._model_class._table).where(
            f"{qb._quote(pk)} = {qb._ph()}", id
        )
        sql, params = qb.build()
        result = await self._driver.execute(sql, params)
        return result.error is None

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        qb = QueryBuilder(dialect=self._driver.dialect)
        qb.select("COUNT(*) as cnt").from_table(self._model_class._table)
        if filters:
            for key, value in filters.items():
                qb.where(f"{qb._quote(key)} = {qb._ph()}", value)
        sql, params = qb.build()
        rows = await self._driver.execute_query(sql, params)
        if rows:
            return int(rows[0].get("cnt", 0))
        return 0


__all__ = [
    "BaseRepository",
]
