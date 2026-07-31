from __future__ import annotations

from typing import Any

from backend.database.models.knowledge import KnowledgeBase, KnowledgeEntry
from backend.exceptions import KnowledgeBaseNotFoundException, KnowledgeIndexException
from backend.repositories.knowledge_repository import (
    KnowledgeBaseRepository,
    KnowledgeChunkRepository,
    KnowledgeEntryRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


class KnowledgeService:
    """Service layer for Knowledge base and entry business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.base_repository = KnowledgeBaseRepository(db)
        self.entry_repository = KnowledgeEntryRepository(db)
        self.chunk_repository = KnowledgeChunkRepository(db)

    # ── Knowledge Base Methods ───────────────────────────────────

    async def get_knowledge_base(self, kb_id: str) -> KnowledgeBase:
        """Get a knowledge base by ID."""
        kb = await self.base_repository.get_by_id(kb_id)
        if not kb:
            raise KnowledgeBaseNotFoundException()
        return kb

    async def create_knowledge_base(
        self,
        project_id: str,
        created_by: str,
        name: str,
        **kwargs: Any,
    ) -> KnowledgeBase:
        """Create a new knowledge base."""
        return await self.base_repository.create(
            project_id=project_id,
            created_by=created_by,
            name=name,
            **kwargs,
        )

    async def update_knowledge_base(self, kb_id: str, **kwargs: Any) -> KnowledgeBase:
        """Update knowledge base fields."""
        await self.get_knowledge_base(kb_id)
        updated = await self.base_repository.update(kb_id, **kwargs)
        if not updated:
            raise KnowledgeBaseNotFoundException()
        return updated

    async def list_knowledge_bases(
        self,
        project_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[KnowledgeBase], int]:
        """List knowledge bases, optionally filtered by project."""
        if project_id:
            return await self.base_repository.get_by_project(project_id, page, page_size)
        return await self.base_repository.list(page=page, page_size=page_size)

    async def delete_knowledge_base(self, kb_id: str) -> bool:
        """Delete a knowledge base and all its entries."""
        await self.get_knowledge_base(kb_id)
        return await self.base_repository.delete(kb_id)

    # ── Knowledge Entry Methods ──────────────────────────────────

    async def get_entry(self, entry_id: str) -> KnowledgeEntry:
        """Get a knowledge entry by ID."""
        entry = await self.entry_repository.get_by_id(entry_id)
        if not entry:
            raise KnowledgeIndexException(detail="Entry not found")
        return entry

    async def create_entry(
        self,
        knowledge_base_id: str,
        created_by: str,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> KnowledgeEntry:
        """Create a new knowledge entry and index it."""
        await self.get_knowledge_base(knowledge_base_id)
        entry = await self.entry_repository.create(
            knowledge_base_id=knowledge_base_id,
            created_by=created_by,
            title=title,
            content=content,
            **kwargs,
        )
        return entry

    async def update_entry(self, entry_id: str, **kwargs: Any) -> KnowledgeEntry:
        """Update a knowledge entry."""
        await self.get_entry(entry_id)
        updated = await self.entry_repository.update(entry_id, **kwargs)
        if not updated:
            raise KnowledgeIndexException(detail="Entry not found")
        return updated

    async def list_entries(
        self,
        knowledge_base_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[KnowledgeEntry], int]:
        """List entries, optionally filtered by knowledge base."""
        if knowledge_base_id:
            return await self.entry_repository.get_by_knowledge_base(knowledge_base_id, page, page_size)
        return await self.entry_repository.list(page=page, page_size=page_size)

    async def search_entries(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[KnowledgeEntry], int]:
        """Search entries by title or content."""
        return await self.entry_repository.search(query, page=page, page_size=page_size)

    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a knowledge entry and its chunks."""
        await self.get_entry(entry_id)
        return await self.entry_repository.delete(entry_id)
