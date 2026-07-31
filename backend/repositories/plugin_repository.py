from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.plugin import Plugin
from backend.repositories.base_repository import BaseRepository


class PluginRepository(BaseRepository[Plugin]):
    """Repository for Plugin entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Plugin)

    async def get_by_project(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Plugin], int]:
        """List plugins installed in a project."""
        return await self.list(page=page, page_size=page_size, filters={"project_id": project_id})

    async def get_by_slug(self, project_id: str, slug: str) -> Plugin | None:
        """Find a specific plugin by project and slug."""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.slug == slug,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_status(
        self,
        status: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Plugin], int]:
        """List plugins with a specific status."""
        return await self.list(page=page, page_size=page_size, filters={"status": status})

    async def get_enabled(self, project_id: str) -> list[Plugin]:
        """Get all enabled plugins for a project."""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.status == "enabled",
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def slug_exists(self, project_id: str, slug: str, exclude_id: str | None = None) -> bool:
        """Check if a plugin slug is already taken within a project."""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(
                self.model.project_id == project_id,
                self.model.slug == slug,
            )
        )
        if exclude_id:
            query = query.where(self.model.id != exclude_id)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0
