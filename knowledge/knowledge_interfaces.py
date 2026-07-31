from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from .knowledge_models import (
    Chunk,
    DocumentRecord,
    Embedding,
    KnowledgeItem,
    MemoryRecord,
    SearchResult,
)


class MemoryStore(ABC):
    """Persistence contract for memory records."""

    @abstractmethod
    def save(self, record: MemoryRecord) -> str: ...

    @abstractmethod
    def get(self, record_id: str) -> MemoryRecord | None: ...

    @abstractmethod
    def list(self, memory_type: str | None = None) -> list[MemoryRecord]: ...

    @abstractmethod
    def delete(self, record_id: str) -> bool: ...

    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def count(self) -> int: ...


class DocumentStore(ABC):
    """Persistence contract for documents."""

    @abstractmethod
    def add(self, document: DocumentRecord) -> str: ...

    @abstractmethod
    def get(self, document_id: str) -> DocumentRecord | None: ...

    @abstractmethod
    def update(self, document_id: str, document: DocumentRecord) -> bool: ...

    @abstractmethod
    def delete(self, document_id: str) -> bool: ...

    @abstractmethod
    def list(self) -> list[DocumentRecord]: ...


class EmbeddingProvider(ABC):
    """Contract for text-to-vector embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> list[float]: ...

    @abstractmethod
    def dimensions(self) -> int: ...


class VectorStore(ABC):
    """Contract for vector similarity storage."""

    @abstractmethod
    def add(self, embedding: Embedding) -> str: ...

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int) -> list[SearchResult]: ...

    @abstractmethod
    def delete(self, embedding_id: str) -> bool: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def clear(self) -> None: ...


class Chunker(ABC):
    """Contract for splitting text into chunks."""

    @abstractmethod
    def chunk(self, text: str, document_id: str = "") -> list[Chunk]: ...


@runtime_checkable
class KnowledgeSink(Protocol):
    """Anything that can consume a knowledge item."""

    def store(self, item: KnowledgeItem) -> str: ...
