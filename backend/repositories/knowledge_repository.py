from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.knowledge import KnowledgeBase, KnowledgeChunk, KnowledgeEntry
from backend.repositories.base_repository import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    """Repository for KnowledgeBase entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, KnowledgeBase)

    async def get_by_project(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[KnowledgeBase], int]:
        """List knowledge bases in a project."""
        return await self.list(page=page, page_size=page_size, filters={"project_id": project_id})

    async def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[KnowledgeBase], int]:
        """Search knowledge bases by name or description."""
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

    async def get_public(self, project_id: str) -> list[KnowledgeBase]:
        """Get all public knowledge bases for a project."""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.is_public == True,
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class KnowledgeEntryRepository(BaseRepository[KnowledgeEntry]):
    """Repository for KnowledgeEntry entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, KnowledgeEntry)

    async def get_by_knowledge_base(
        self,
        kb_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[KnowledgeEntry], int]:
        """List entries in a knowledge base."""
        return await self.list(page=page, page_size=page_size, filters={"knowledge_base_id": kb_id})

    async def search(
        self,
        query_str: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[KnowledgeEntry], int]:
        """Search entries by title or content."""
        pattern = f"%{query_str}%"
        where_clause = (self.model.title.ilike(pattern)) | (self.model.content.ilike(pattern))

        query = select(self.model).where(where_clause)
        count_query = select(func.count()).select_from(self.model).where(where_clause)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def search_by_tags(self, tags: list[str]) -> list[KnowledgeEntry]:
        """Find entries containing any of the specified tags."""
        query = select(self.model).where(self.model.tags.overlap(tags))
        result = await self.db.execute(query)
        return list(result.scalars().all())


class KnowledgeChunkRepository(BaseRepository[KnowledgeChunk]):
    """Repository for KnowledgeChunk entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, KnowledgeChunk)

    async def get_by_entry(self, entry_id: str) -> list[KnowledgeChunk]:
        """Get all chunks for a specific entry, ordered by index."""
        query = (
            select(self.model)
            .where(self.model.entry_id == entry_id)
            .order_by(self.model.chunk_index)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_entry_batch(self, entry_ids: list[str]) -> list[KnowledgeChunk]:
        """Get all chunks for multiple entries."""
        query = (
            select(self.model)
            .where(self.model.entry_id.in_(entry_ids))
            .order_by(self.model.entry_id, self.model.chunk_index)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
