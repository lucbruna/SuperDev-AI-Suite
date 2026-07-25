from __future__ import annotations

from typing import Any, TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.base_repository import BaseRepository
from backend.database.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseService(Generic[T]):
    """Base service layer for business logic."""

    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.repository = BaseRepository(db, model)

    async def get(self, id: str) -> T | None:
        return await self.repository.get_by_id(id)

    async def create(self, **kwargs) -> T:
        return await self.repository.create(**kwargs)

    async def update(self, id: str, **kwargs) -> T | None:
        return await self.repository.update(id, **kwargs)

    async def delete(self, id: str) -> bool:
        return await self.repository.delete(id)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[T], int]:
        return await self.repository.list(page=page, page_size=page_size, filters=filters)

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        return await self.repository.count(filters)

    async def exists(self, id: str) -> bool:
        return await self.repository.exists(id)
