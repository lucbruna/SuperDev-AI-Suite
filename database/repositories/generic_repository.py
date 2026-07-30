from __future__ import annotations

from typing import Any, Generic, TypeVar

from ..orm.model import Model
from ..orm.session import Session
from .base_repository import BaseRepository

M = TypeVar("M", bound=Model)


class GenericRepository(BaseRepository, Generic[M]):
    """Typed repository that provides CRUD operations for a model class.

    Usage::

        repo = GenericRepository[User](session, User)
        user = await repo.get(1)
    """

    def __init__(self, session: Session, model_class: type[M] | None = None) -> None:
        if model_class is not None:
            self._model_class = model_class
        super().__init__(session)

    async def get(self, id: Any) -> M | None:  # type: ignore[override]
        return await super().get(id)  # type: ignore[return-value]

    async def list(self, filters: dict[str, Any] | None = None) -> list[M]:  # type: ignore[override]
        return await super().list(filters)  # type: ignore[return-value]

    async def create(self, entity: M) -> M:  # type: ignore[override]
        return await super().create(entity)  # type: ignore[return-value]

    async def update(self, entity: M) -> M:  # type: ignore[override]
        return await super().update(entity)  # type: ignore[return-value]


__all__ = [
    "GenericRepository",
    "M",
]
