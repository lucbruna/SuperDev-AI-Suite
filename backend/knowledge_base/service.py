from __future__ import annotations

import os
from dataclasses import dataclass
from uuid import UUID

import pathspec
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.knowledge_base.embedding_service import EmbeddingService
from backend.knowledge_base.models import KnowledgeBase, KnowledgeBaseType, KnowledgeChunk, KnowledgeEntry


async def get_knowledge_base_service(db: AsyncSession = Depends(get_db)) -> KnowledgeBaseService:
    return KnowledgeBaseService(db)


@dataclass
class ChunkConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100


@dataclass
class SearchResult:
    entry: KnowledgeEntry
    chunk: KnowledgeChunk
    similarity: float


class VectorStore:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.embedding_service = EmbeddingService()

    async def search(
        self,
        query: str,
        knowledge_base_ids: list[UUID] | None = None,
        top_k: int = 10,
        similarity_threshold: float = 0.5,
    ) -> list[SearchResult]:
        query_embedding = self.embedding_service.embed_text(query)
        
        stmt = (
            select(KnowledgeChunk, KnowledgeEntry, KnowledgeBase)
            .join(KnowledgeEntry, KnowledgeChunk.entry_id == KnowledgeEntry.id)
            .join(KnowledgeBase, KnowledgeEntry.knowledge_base_id == KnowledgeBase.id)
            .where(KnowledgeChunk.embedding.is_not(None))
        )
        
        if knowledge_base_ids:
            stmt = stmt.where(KnowledgeEntry.knowledge_base_id.in_(knowledge_base_ids))
        
        stmt = stmt.order_by(KnowledgeChunk.embedding.cosine_distance(query_embedding)).limit(top_k * 2)
        
        results = await self.session.execute(stmt)
        rows = results.all()
        
        search_results = []
        for chunk, entry, _kb in rows:
            if chunk.embedding is None:
                continue
            
            similarity = 1 - chunk.embedding.cosine_distance(query_embedding)
            if similarity >= similarity_threshold:
                search_results.append(SearchResult(entry=entry, chunk=chunk, similarity=similarity))
        
        search_results.sort(key=lambda x: x.similarity, reverse=True)
        return search_results[:top_k]


class KnowledgeBaseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.vector_store = VectorStore(session)
        self.embedding_service = EmbeddingService()
        self.chunk_config = ChunkConfig()

    async def create_knowledge_base(
        self,
        name: str,
        description: str | None = None,
        type: KnowledgeBaseType = KnowledgeBaseType.DOCUMENTATION,
        is_public: bool = False,
    ) -> KnowledgeBase:
        kb = KnowledgeBase(
            name=name,
            description=description,
            type=type,
            is_public=is_public,
        )
        self.session.add(kb)
        await self.session.flush()
        return kb

    async def add_document(
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
        kb = await self.session.get(KnowledgeBase, knowledge_base_id)
        if not kb:
            raise ValueError(f"Knowledge base {knowledge_base_id} not found")
        
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
        
        await self._create_chunks(entry, content)
        await self.session.commit()
        
        return entry

    async def add_code_file(
        self,
        knowledge_base_id: UUID,
        file_path: str,
        content: str,
        language: str | None = None,
        tags: list[str] | None = None,
    ) -> KnowledgeEntry:
        entry_tags = tags or []
        entry_tags.extend(["code", "repository"])
        
        if language:
            entry_tags.append(language)
        
        return await self.add_document(
            knowledge_base_id=knowledge_base_id,
            title=os.path.basename(file_path),
            content=content,
            source_type="code",
            language=language,
            tags=entry_tags,
            metadata={"file_path": file_path},
        )

    async def _create_chunks(self, entry: KnowledgeEntry, content: str) -> list[KnowledgeChunk]:
        chunks_data = self._split_into_chunks(content)
        
        chunk_texts = [chunk[1] for chunk in chunks_data]
        embeddings = self.embedding_service.embed_texts(chunk_texts)
        
        chunks = []
        for (chunk_index, chunk_content, chunk_metadata), embedding in zip(chunks_data, embeddings, strict=False):
            chunk = KnowledgeChunk(
                entry_id=entry.id,
                chunk_index=chunk_index,
                content=chunk_content,
                token_count=len(chunk_content.split()),
                embedding=embedding,
                metadata=chunk_metadata,
            )
            self.session.add(chunk)
            chunks.append(chunk)
        
        await self.session.flush()
        return chunks

    def _split_into_chunks(self, content: str) -> list[tuple[int, str, dict]]:
        lines = content.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for line in lines:
            line_size = len(line) + 1
            
            if current_size + line_size > self.chunk_config.chunk_size and current_chunk:
                chunk_content = "\n".join(current_chunk)
                if len(chunk_content) >= self.chunk_config.min_chunk_size:
                    chunks.append((chunk_index, chunk_content, {"lines": len(current_chunk)}))
                    chunk_index += 1
                
                overlap_lines = max(1, self.chunk_config.chunk_overlap // (current_size // len(current_chunk)) if current_chunk else 1)
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines < len(current_chunk) else current_chunk
                current_size = sum(len(l) + 1 for l in current_chunk)
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            if len(chunk_content) >= self.chunk_config.min_chunk_size:
                chunks.append((chunk_index, chunk_content, {"lines": len(current_chunk)}))
        
        return chunks

    async def search(
        self,
        query: str,
        knowledge_base_ids: list[UUID] | None = None,
        top_k: int = 10,
        similarity_threshold: float = 0.5,
    ) -> list[SearchResult]:
        return await self.vector_store.search(
            query=query,
            knowledge_base_ids=knowledge_base_ids,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

    async def find_similar_code(
        self,
        code_snippet: str,
        language: str | None = None,
        knowledge_base_ids: list[UUID] | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        query = f"```{language or ''}\n{code_snippet}\n```" if language else code_snippet
        
        results = await self.search(
            query=query,
            knowledge_base_ids=knowledge_base_ids,
            top_k=top_k * 2,
        )
        
        if language:
            results = [r for r in results if r.entry.language == language]
        
        return results[:top_k]

    async def get_context_for_query(
        self,
        query: str,
        knowledge_base_ids: list[UUID] | None = None,
        max_tokens: int = 8000,
    ) -> str:
        results = await self.search(
            query=query,
            knowledge_base_ids=knowledge_base_ids,
            top_k=20,
            similarity_threshold=0.4,
        )
        
        context_parts = []
        total_tokens = 0
        
        for result in results:
            chunk_text = f"Source: {result.entry.title}\n{result.chunk.content}\n---\n"
            chunk_tokens = len(chunk_text.split())
            
            if total_tokens + chunk_tokens > max_tokens:
                break
            
            context_parts.append(chunk_text)
            total_tokens += chunk_tokens
        
        return "\n".join(context_parts)

    async def ingest_repository(
        self,
        knowledge_base_id: UUID,
        repo_path: str,
        file_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> int:
        if file_patterns is None:
            file_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "*.cpp", "*.h", "*.cs", "*.php", "*.rb", "*.swift", "*.kt"]
        
        if exclude_patterns is None:
            exclude_patterns = [".git", "__pycache__", "node_modules", "dist", "build", "*.pyc", ".venv", "venv", "target"]
        
        spec = pathspec.PathSpec.from_lines("gitwildmatch", exclude_patterns)
        pattern_specs = [pathspec.PathSpec.from_lines("gitwildmatch", [p]) for p in file_patterns]
        
        count = 0
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.relpath(os.path.join(root, d), repo_path))]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                if not any(ps.match_file(rel_path) for ps in pattern_specs):
                    continue
                
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                    
                    if not content.strip():
                        continue
                    
                    ext = os.path.splitext(file)[1].lstrip(".")
                    language = self._get_language_from_extension(ext)
                    
                    await self.add_code_file(
                        knowledge_base_id=knowledge_base_id,
                        file_path=rel_path,
                        content=content,
                        language=language,
                    )
                    count += 1
                except Exception:
                    continue
        
        await self.session.commit()
        return count

    def _get_language_from_extension(self, ext: str) -> str:
        lang_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "javascript",
            "tsx": "typescript",
            "java": "java",
            "go": "go",
            "rs": "rust",
            "cpp": "cpp",
            "cc": "cpp",
            "cxx": "cpp",
            "c": "c",
            "h": "c",
            "hpp": "cpp",
            "cs": "csharp",
            "php": "php",
            "rb": "ruby",
            "swift": "swift",
            "kt": "kotlin",
            "scala": "scala",
            "r": "r",
            "sql": "sql",
            "sh": "bash",
            "bash": "bash",
            "zsh": "bash",
            "fish": "fish",
            "ps1": "powershell",
            "yaml": "yaml",
            "yml": "yaml",
            "json": "json",
            "xml": "xml",
            "html": "html",
            "css": "css",
            "scss": "scss",
            "less": "less",
            "md": "markdown",
            "txt": "text",
            "dockerfile": "dockerfile",
            "tf": "terraform",
            "proto": "protobuf",
        }
        return lang_map.get(ext.lower(), "text")