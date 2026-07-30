from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.project import Project
from backend.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Project)

    async def get_by_slug(self, slug: str) -> Project | None:
        """Find a project by its URL slug."""
        query = select(self.model).where(self.model.slug == slug)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_organization(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """List projects belonging to an organization."""
        filters = {"organization_id": org_id}
        return await self.list(page=page, page_size=page_size, filters=filters)

    async def get_by_owner(
        self,
        owner_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """List projects owned by a specific user."""
        filters = {"owner_id": owner_id}
        return await self.list(page=page, page_size=page_size, filters=filters)

    async def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """Search projects by name or description."""
        pattern = f"%{query_str}%"
        where_clause = (self.model.name.ilike(pattern)) | (self.model.description.ilike(pattern))

        query = select(self.model).where(where_clause)
        count_query = select(func.count()).select_from(self.model).where(where_clause)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_visibility(
        self,
        visibility: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """List projects filtered by visibility."""
        return await self.list(page=page, page_size=page_size, filters={"visibility": visibility})

    async def slug_exists(self, slug: str, exclude_id: str | None = None) -> bool:
        """Check if a slug is already taken."""
        query = select(func.count()).select_from(self.model).where(self.model.slug == slug)
        if exclude_id:
            query = query.where(self.model.id != exclude_id)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0
