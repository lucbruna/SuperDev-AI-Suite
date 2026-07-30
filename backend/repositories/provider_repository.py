from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.provider import Provider
from backend.repositories.base_repository import BaseRepository


class ProviderRepository(BaseRepository[Provider]):
    """Repository for Provider entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Provider)

    async def get_by_project(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Provider], int]:
        """List providers configured for a project."""
        return await self.list(page=page, page_size=page_size, filters={"project_id": project_id})

    async def get_by_type(
        self,
        provider_type: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Provider], int]:
        """List providers of a specific type."""
        return await self.list(page=page, page_size=page_size, filters={"type": provider_type})

    async def get_defaults(self, project_id: str) -> list[Provider]:
        """Get all default providers for a project."""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.is_default == True,
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_by_project(self, project_id: str) -> list[Provider]:
        """Get all active providers for a project, ordered by priority."""
        query = (
            select(self.model)
            .where(
                self.model.project_id == project_id,
                self.model.is_active == True,
            )
            .order_by(self.model.priority.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_by_type(self, project_id: str, provider_type: str) -> Provider | None:
        """Get the active provider of a specific type for a project."""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.type == provider_type,
            self.model.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
