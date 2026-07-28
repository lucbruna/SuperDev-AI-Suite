from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.knowledge_base.embedding_service import embedding_service
from backend.knowledge_base.models import KnowledgeBase, KnowledgeChunk, KnowledgeEntry


@dataclass
class SearchResult:
    chunk: KnowledgeChunk
    entry: KnowledgeEntry
    knowledge_base: KnowledgeBase
    score: float


class VectorStore:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_knowledge_base(
        self,
        name: str,
        description: str | None = None,
        kb_type: str = "documentation",
        is_public: bool = False,
    ) -> KnowledgeBase:
        kb = KnowledgeBase(
            name=name,
            description=description,
            type=kb_type,
            is_public=is_public,
        )
        self.session.add(kb)
        await self.session.flush()
        return kb

    async def add_entry(
        self,
        knowledge_base_id: UUID,
        title: str,
        content: str,
        source_url: str | None = None,
        source_type: str | None = None,
        language: str | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> KnowledgeEntry:
        entry = KnowledgeEntry(
            knowledge_base_id=knowledge_base_id,
            title=title,
            content=content,
            source_url=source_url,
            source_type=source_type,
            language=language,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def add_chunks(
        self,
        entry_id: UUID,
        chunks: list[tuple[int, str, dict | None]],
    ) -> list[KnowledgeChunk]:
        knowledge_chunks = []
        for chunk_index, content, metadata in chunks:
            if not content.strip():
                continue
            
            embedding = embedding_service.embed_text(content)
            
            chunk = KnowledgeChunk(
                entry_id=entry_id,
                chunk_index=chunk_index,
                content=content,
                token_count=len(content.split()),
                embedding=embedding,
extra_metadata=metadata or {},
            )
            knowledge_chunks.append(chunk)
        
        self.session.add_all(knowledge_chunks)
        await self.session.flush()
        return knowledge_chunks

    async def search(
        self,
        query: str,
        knowledge_base_ids: list[UUID] | None = None,
        top_k: int = 10,
        similarity_threshold: float = 0.5,
    ) -> list[SearchResult]:
        query_embedding = embedding_service.embed_text(query)
        
        where_clause = "1=1"
        params = {"query_embedding": query_embedding, "top_k": top_k, "threshold": similarity_threshold}
        
        if knowledge_base_ids:
            kb_ids_str = ",".join(f"'{kb_id}'" for kb_id in knowledge_base_ids)
            where_clause = f"kb.id IN ({kb_ids_str})"

        sql = text(f"""
            SELECT 
                c.id as chunk_id,
                c.entry_id,
                c.chunk_index,
                c.content as chunk_content,
                c.token_count,
                c.metadata as chunk_metadata,
                c.created_at as chunk_created_at,
                e.id as entry_id,
                e.knowledge_base_id,
                e.title,
                e.content as entry_content,
                e.source_url,
                e.source_type,
                e.language,
                e.tags,
                e.metadata as entry_metadata,
                e.created_at as entry_created_at,
                e.updated_at as entry_updated_at,
                kb.id as kb_id,
                kb.name as kb_name,
                kb.description as kb_description,
                kb.type as kb_type,
                kb.is_public as kb_is_public,
                kb.created_at as kb_created_at,
                kb.updated_at as kb_updated_at,
                1 - (c.embedding <=> :query_embedding) as similarity
            FROM knowledge_chunks c
            JOIN knowledge_entries e ON c.entry_id = e.id
            JOIN knowledge_bases kb ON e.knowledge_base_id = kb.id
            WHERE {where_clause}
            AND c.embedding IS NOT NULL
            AND 1 - (c.embedding <=> :query_embedding) >= :threshold
            ORDER BY c.embedding <=> :query_embedding
            LIMIT :top_k
        """)
        
        result = await self.session.execute(sql, params)
        rows = result.mappings().all()
        
        search_results = []
        for row in rows:
            chunk = KnowledgeChunk(
                id=row["chunk_id"],
                entry_id=row["entry_id"],
                chunk_index=row["chunk_index"],
                content=row["chunk_content"],
                token_count=row["token_count"],
                metadata=row["chunk_metadata"],
                created_at=row["chunk_created_at"],
            )
            
            entry = KnowledgeEntry(
                id=row["entry_id"],
                knowledge_base_id=row["knowledge_base_id"],
                title=row["title"],
                content=row["entry_content"],
                source_url=row["source_url"],
                source_type=row["source_type"],
                language=row["language"],
                tags=row["tags"],
                metadata=row["entry_metadata"],
                created_at=row["entry_created_at"],
                updated_at=row["entry_updated_at"],
            )
            
            kb = KnowledgeBase(
                id=row["kb_id"],
                name=row["kb_name"],
                description=row["kb_description"],
                type=row["kb_type"],
                is_public=row["kb_is_public"],
                created_at=row["kb_created_at"],
                updated_at=row["kb_updated_at"],
            )
            
            search_results.append(SearchResult(
                chunk=chunk,
                entry=entry,
                knowledge_base=kb,
                score=row["similarity"],
            ))
        
        return search_results

    async def search_by_entry(
        self,
        entry_id: UUID,
        top_k: int = 5,
    ) -> list[SearchResult]:
        sql = text("""
            SELECT 
                c.id as chunk_id,
                c.entry_id,
                c.chunk_index,
                c.content as chunk_content,
                c.token_count,
                c.metadata as chunk_metadata,
                c.created_at as chunk_created_at,
                e.id as entry_id,
                e.knowledge_base_id,
                e.title,
                e.content as entry_content,
                e.source_url,
                e.source_type,
                e.language,
                e.tags,
                e.metadata as entry_metadata,
                e.created_at as entry_created_at,
                e.updated_at as entry_updated_at,
                kb.id as kb_id,
                kb.name as kb_name,
                kb.description as kb_description,
                kb.type as kb_type,
                kb.is_public as kb_is_public,
                kb.created_at as kb_created_at,
                kb.updated_at as kb_updated_at,
                1 - (c.embedding <=> c2.embedding) as similarity
            FROM knowledge_chunks c
            JOIN knowledge_chunks c2 ON c2.entry_id = :entry_id AND c2.chunk_index = 0
            JOIN knowledge_entries e ON c.entry_id = e.id
            JOIN knowledge_bases kb ON e.knowledge_base_id = kb.id
            WHERE c.entry_id != :entry_id
            AND c.embedding IS NOT NULL
            ORDER BY c.embedding <=> c2.embedding
            LIMIT :top_k
        """)
        
        result = await self.session.execute(sql, {"entry_id": entry_id, "top_k": top_k})
        rows = result.mappings().all()
        
        search_results = []
        for row in rows:
            chunk = KnowledgeChunk(
                id=row["chunk_id"],
                entry_id=row["entry_id"],
                chunk_index=row["chunk_index"],
                content=row["chunk_content"],
                token_count=row["token_count"],
                metadata=row["chunk_metadata"],
                created_at=row["chunk_created_at"],
            )
            
            entry = KnowledgeEntry(
                id=row["entry_id"],
                knowledge_base_id=row["knowledge_base_id"],
                title=row["title"],
                content=row["entry_content"],
                source_url=row["source_url"],
                source_type=row["source_type"],
                language=row["language"],
                tags=row["tags"],
                metadata=row["entry_metadata"],
                created_at=row["entry_created_at"],
                updated_at=row["entry_updated_at"],
            )
            
            kb = KnowledgeBase(
                id=row["kb_id"],
                name=row["kb_name"],
                description=row["kb_description"],
                type=row["kb_type"],
                is_public=row["kb_is_public"],
                created_at=row["kb_created_at"],
                updated_at=row["kb_updated_at"],
            )
            
            search_results.append(SearchResult(
                chunk=chunk,
                entry=entry,
                knowledge_base=kb,
                score=row["similarity"],
            ))
        
        return search_results

    async def delete_entry(self, entry_id: UUID) -> bool:
        entry = await self.session.get(KnowledgeEntry, entry_id)
        if entry:
            await self.session.delete(entry)
            return True
        return False

    async def delete_knowledge_base(self, kb_id: UUID) -> bool:
        kb = await self.session.get(KnowledgeBase, kb_id)
        if kb:
            await self.session.delete(kb)
            return True
        return False

    async def get_knowledge_base(self, kb_id: UUID) -> KnowledgeBase | None:
        return await self.session.get(KnowledgeBase, kb_id)

    async def list_knowledge_bases(
        self,
        is_public: bool | None = None,
        kb_type: str | None = None,
    ) -> list[KnowledgeBase]:
        query = select(KnowledgeBase)
        
        if is_public is not None:
            query = query.where(KnowledgeBase.is_public == is_public)
        if kb_type:
            query = query.where(KnowledgeBase.type == kb_type)
        
        query = query.order_by(KnowledgeBase.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_entry(self, entry_id: UUID) -> KnowledgeEntry | None:
        return await self.session.get(KnowledgeEntry, entry_id)

    async def list_entries(
        self,
        knowledge_base_id: UUID | None = None,
        tags: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeEntry]:
        query = select(KnowledgeEntry)
        
        if knowledge_base_id:
            query = query.where(KnowledgeEntry.knowledge_base_id == knowledge_base_id)
        if tags:
            query = query.where(KnowledgeEntry.tags.overlap(tags))
        
        query = query.order_by(KnowledgeEntry.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())