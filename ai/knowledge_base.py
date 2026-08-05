from __future__ import annotations

import asyncio
import functools
import hashlib
import json
import logging
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from core.configuration import settings

logger = logging.getLogger("superdev.ai.knowledge")


class ChunkingStrategy(str, Enum):
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"


@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    batch_size: int = 32
    max_seq_length: int = 256
    normalize_embeddings: bool = True


@dataclass
class Document:
    doc_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: Optional[list[float]] = None
    chunk_index: int = 0
    parent_id: Optional[str] = None
    source: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content[:1000],
            "metadata": self.metadata,
            "chunk_index": self.chunk_index,
            "parent_id": self.parent_id,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SearchResult:
    document: Document
    score: float = 0.0
    rank: int = 0
    matched_chunks: list[str] = field(default_factory=list)
    search_type: str = "semantic"

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.document.doc_id,
            "content": self.document.content[:500],
            "score": round(self.score, 4),
            "rank": self.rank,
            "source": self.document.source,
            "search_type": self.search_type,
        }


class LRUCache:
    def __init__(self, capacity: int = 1000, ttl_seconds: float = 3600):
        self._capacity = capacity
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, expiry = self._cache[key]
        if time.monotonic() > expiry:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        expiry = time.monotonic() + (ttl or self._ttl)
        self._cache[key] = (value, expiry)
        self._cache.move_to_end(key)
        self._evict()

    def _evict(self) -> None:
        while len(self._cache) > self._capacity:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()

    def remove(self, key: str) -> None:
        self._cache.pop(key, None)

    @property
    def size(self) -> int:
        return len(self._cache)


class EmbeddingModel:
    def __init__(self, config: Optional[EmbeddingConfig] = None) -> None:
        self._config = config or EmbeddingConfig()
        self._model: Any = None
        self._model_loaded = False

    def _load_model(self) -> None:
        if self._model_loaded:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self._config.model_name,
                device=self._config.device,
            )
            self._model.max_seq_length = self._config.max_seq_length
            self._model_loaded = True
            logger.info("Loaded embedding model: %s", self._config.model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required. Install with: pip install sentence-transformers"
            )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self._load_model()
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            functools.partial(
                self._model.encode,
                texts,
                batch_size=self._config.batch_size,
                normalize_embeddings=self._config.normalize_embeddings,
                show_progress_bar=False,
            ),
        )
        return [emb.tolist() for emb in embeddings]

    async def embed_query(self, text: str) -> list[float]:
        embeddings = await self.embed([text])
        return embeddings[0]

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class DocumentChunker:
    def __init__(self, strategy: ChunkingStrategy = ChunkingStrategy.PARAGRAPH, chunk_size: int = 512, overlap: int = 50):
        self._strategy = strategy
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str, source: str = "", metadata: Optional[dict[str, Any]] = None) -> list[Document]:
        metadata = metadata or {}
        chunks: list[Document] = []

        if self._strategy == ChunkingStrategy.PARAGRAPH:
            raw_chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
            for i, chunk_text in enumerate(raw_chunks):
                if len(chunk_text) > self._chunk_size * 2:
                    sub_chunks = self._fixed_size_chunk(chunk_text)
                    for j, sub in enumerate(sub_chunks):
                        chunks.append(self._make_doc(sub, source, metadata, i + j))
                else:
                    chunks.append(self._make_doc(chunk_text, source, metadata, i))

        elif self._strategy == ChunkingStrategy.SENTENCE:
            import re
            sentences = re.split(r"(?<=[.!?])\s+", text)
            current = ""
            for sent in sentences:
                if not sent.strip():
                    continue
                if len(current) + len(sent) > self._chunk_size and current:
                    chunks.append(self._make_doc(current.strip(), source, metadata, len(chunks)))
                    current = sent
                else:
                    current = f"{current} {sent}".strip()
            if current:
                chunks.append(self._make_doc(current.strip(), source, metadata, len(chunks)))

        elif self._strategy == ChunkingStrategy.FIXED_SIZE:
            raw = self._fixed_size_chunk(text)
            for i, chunk_text in enumerate(raw):
                chunks.append(self._make_doc(chunk_text, source, metadata, i))

        elif self._strategy == ChunkingStrategy.RECURSIVE:
            separators = ["\n\n", "\n", ". ", " ", ""]
            chunks = self._recursive_chunk(text, separators, source, metadata)

        if not chunks:
            chunks.append(self._make_doc(text, source, metadata, 0))

        return chunks

    def _fixed_size_chunk(self, text: str) -> list[str]:
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + self._chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self._overlap
        return chunks

    def _recursive_chunk(
        self, text: str, separators: list[str], source: str, metadata: dict[str, Any]
    ) -> list[Document]:
        if len(text) <= self._chunk_size:
            return [self._make_doc(text, source, metadata, 0)]

        for sep in separators:
            if not sep:
                parts = [text[i:i + self._chunk_size] for i in range(0, len(text), self._chunk_size)]
                return [self._make_doc(p, source, metadata, i) for i, p in enumerate(parts)]
            if sep in text:
                parts = text.split(sep)
                chunks: list[Document] = []
                current = ""
                for part in parts:
                    if not part.strip():
                        continue
                    if len(current) + len(part) > self._chunk_size and current:
                        chunks.append(self._make_doc(current.strip(), source, metadata, len(chunks)))
                        current = part
                    else:
                        current = f"{current}{sep}{part}".strip()
                if current:
                    chunks.append(self._make_doc(current.strip(), source, metadata, len(chunks)))
                return chunks

        return [self._make_doc(text, source, metadata, 0)]

    def _make_doc(self, content: str, source: str, metadata: dict[str, Any], index: int) -> Document:
        return Document(
            content=content.strip(),
            metadata=metadata,
            chunk_index=index,
            source=source,
        )


class ElasticsearchStore:
    def __init__(self, hosts: Optional[list[str]] = None, index_prefix: str = "superdev_kb") -> None:
        self._hosts = hosts or settings.elasticsearch.hosts
        self._index_prefix = index_prefix
        self._client: Any = None
        self._available = False

    async def _ensure_connected(self) -> None:
        if self._available:
            return
        try:
            from elasticsearch import AsyncElasticsearch
            self._client = AsyncElasticsearch(
                hosts=self._hosts,
                basic_auth=(
                    settings.elasticsearch.username,
                    settings.elasticsearch.password,
                ) if settings.elasticsearch.username else None,
                verify_certs=settings.elasticsearch.verify_certs,
                ssl_show_warn=False,
            )
            await self._client.info()
            self._available = True
            logger.info("Connected to Elasticsearch at %s", self._hosts)
        except Exception as exc:
            logger.warning("Elasticsearch unavailable: %s", exc)
            self._available = False

    async def index_document(self, doc: Document, index: str = "documents") -> bool:
        if not self._available:
            return False
        await self._ensure_connected()
        try:
            await self._client.index(
                index=f"{self._index_prefix}_{index}",
                id=doc.doc_id,
                body={
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "source": doc.source,
                    "chunk_index": doc.chunk_index,
                    "created_at": doc.created_at.isoformat(),
                },
                refresh="wait_for",
            )
            return True
        except Exception as exc:
            logger.error("ES index error: %s", exc)
            return False

    async def search(
        self, query: str, index: str = "documents", size: int = 10
    ) -> list[SearchResult]:
        if not self._available:
            return []
        await self._ensure_connected()
        try:
            response = await self._client.search(
                index=f"{self._index_prefix}_{index}",
                body={
                    "query": {
                        "match": {
                            "content": {
                                "query": query,
                                "fuzziness": "AUTO",
                            }
                        }
                    },
                    "size": size,
                },
            )
            results: list[SearchResult] = []
            for i, hit in enumerate(response["hits"]["hits"]):
                source = hit["_source"]
                doc = Document(
                    doc_id=hit["_id"],
                    content=source["content"],
                    metadata=source.get("metadata", {}),
                    source=source.get("source", ""),
                    chunk_index=source.get("chunk_index", 0),
                )
                results.append(
                    SearchResult(
                        document=doc,
                        score=hit["_score"],
                        rank=i + 1,
                        search_type="fulltext",
                    )
                )
            return results
        except Exception as exc:
            logger.error("ES search error: %s", exc)
            return []

    async def delete_index(self, index: str = "documents") -> bool:
        if not self._available:
            return False
        try:
            await self._client.indices.delete(
                index=f"{self._index_prefix}_{index}", ignore_unavailable=True
            )
            return True
        except Exception:
            return False

    async def close(self) -> None:
        if self._client:
            await self._client.close()


class KnowledgeBase:
    def __init__(
        self,
        embedding_config: Optional[EmbeddingConfig] = None,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.PARAGRAPH,
        chunk_size: int = 512,
        overlap: int = 50,
        cache_capacity: int = 1000,
        cache_ttl: float = 3600.0,
        use_elasticsearch: bool = True,
    ) -> None:
        self._embedder = EmbeddingModel(embedding_config)
        self._chunker = DocumentChunker(chunking_strategy, chunk_size, overlap)
        self._cache = LRUCache(capacity=cache_capacity, ttl_seconds=cache_ttl)
        self._documents: dict[str, Document] = {}
        self._embeddings: dict[str, list[float]] = {}
        self._es: Optional[ElasticsearchStore] = ElasticsearchStore() if use_elasticsearch else None

    async def add_text(
        self,
        text: str,
        source: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[str]:
        chunks = self._chunker.chunk(text, source, metadata)

        texts = [c.content for c in chunks]
        embeddings = await self._embedder.embed(texts)

        doc_ids: list[str] = []
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            chunk.embedding = embedding
            self._documents[chunk.doc_id] = chunk
            self._embeddings[chunk.doc_id] = embedding
            doc_ids.append(chunk.doc_id)

            if self._es:
                await self._es.index_document(chunk)

        logger.info("Indexed %d chunks from '%s'", len(chunks), source or text[:50])
        return doc_ids

    async def add_document(self, document: Document) -> str:
        doc_id = document.doc_id or uuid.uuid4().hex
        document.doc_id = doc_id

        embedding = await self._embedder.embed([document.content])
        document.embedding = embedding[0]

        self._documents[doc_id] = document
        self._embeddings[doc_id] = document.embedding

        if self._es:
            await self._es.index_document(document)

        return doc_id

    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.3,
    ) -> list[SearchResult]:
        cache_key = f"semantic:{hashlib.md5(query.encode()).hexdigest()}:{top_k}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if not self._embeddings:
            return []

        query_embedding = await self._embedder.embed_query(query)

        scored: list[tuple[str, float]] = []
        for doc_id, emb in self._embeddings.items():
            score = self._embedder.cosine_similarity(query_embedding, emb)
            if score >= min_score:
                scored.append((doc_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        scored = scored[:top_k]

        results = [
            SearchResult(
                document=self._documents[doc_id],
                score=score,
                rank=i + 1,
                search_type="semantic",
            )
            for i, (doc_id, score) in enumerate(scored)
        ]

        self._cache.set(cache_key, results, ttl=300)
        return results

    async def fulltext_search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[SearchResult]:
        if self._es:
            results = await self._es.search(query, size=top_k)
            if results:
                return results

        query_lower = query.lower()
        query_terms = query_lower.split()
        scored: list[tuple[str, float]] = []

        for doc_id, doc in self._documents.items():
            content_lower = doc.content.lower()
            score = 0.0
            for term in query_terms:
                count = content_lower.count(term)
                score += count * (1.0 / len(query_terms))
            if score > 0:
                scored.append((doc_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        scored = scored[:top_k]

        return [
            SearchResult(
                document=self._documents[doc_id],
                score=score,
                rank=i + 1,
                search_type="fulltext",
            )
            for i, (doc_id, score) in enumerate(scored)
        ]

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        semantic_weight: float = 0.7,
    ) -> list[SearchResult]:
        semantic_results = await self.semantic_search(query, top_k=top_k * 2)
        fulltext_results = await self.fulltext_search(query, top_k=top_k * 2)

        combined: dict[str, SearchResult] = {}

        for i, r in enumerate(semantic_results):
            r.score *= semantic_weight
            r.rank = i + 1
            combined[r.document.doc_id] = r

        for i, r in enumerate(fulltext_results):
            adjusted = r.score * (1.0 - semantic_weight)
            if r.document.doc_id in combined:
                combined[r.document.doc_id].score += adjusted
            else:
                r.score = adjusted
                r.rank = i + 1
                combined[r.document.doc_id] = r

        results = sorted(combined.values(), key=lambda r: r.score, reverse=True)[:top_k]
        for i, r in enumerate(results):
            r.rank = i + 1
            r.search_type = "hybrid"

        return results

    async def retrieve_context(
        self,
        query: str,
        max_tokens: int = 2000,
        top_k: int = 5,
    ) -> str:
        results = await self.hybrid_search(query, top_k=top_k)

        context_parts: list[str] = []
        token_estimate = 0

        for result in results:
            content = result.document.content
            content_tokens = len(content) // 4
            if token_estimate + content_tokens > max_tokens:
                remaining_chars = max_tokens * 4 - token_estimate * 4
                if remaining_chars > 50:
                    context_parts.append(content[:remaining_chars])
                break
            context_parts.append(content)
            token_estimate += content_tokens

        if not context_parts:
            return ""

        header = f"Context retrieved for: {query}\n{'-' * 40}\n"
        return header + "\n\n".join(context_parts)

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self._documents.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self._documents:
            del self._documents[doc_id]
            self._embeddings.pop(doc_id, None)
            self._cache.remove(f"semantic:{doc_id}")
            return True
        return False

    def clear(self) -> None:
        self._documents.clear()
        self._embeddings.clear()
        self._cache.clear()
        logger.info("Knowledge base cleared")

    @property
    def document_count(self) -> int:
        return len(self._documents)

    def stats(self) -> dict[str, Any]:
        return {
            "document_count": self.document_count,
            "embedding_dimension": len(next(iter(self._embeddings.values()))) if self._embeddings else 0,
            "cache_size": self._cache.size,
            "elasticsearch_enabled": self._es is not None,
        }

    async def close(self) -> None:
        if self._es:
            await self._es.close()
