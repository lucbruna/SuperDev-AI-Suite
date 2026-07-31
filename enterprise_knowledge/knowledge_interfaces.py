"""Interfaces (ABCs) for the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from enterprise_knowledge.knowledge_models import (DocumentRecord,
                                                   KnowledgeNode,
                                                   MemoryRecord,
                                                   RelationshipRecord)


class GraphStore(ABC):
    @abstractmethod
    def upsert_node(self, node: KnowledgeNode) -> None: ...

    @abstractmethod
    def add_relationship(self, relationship: RelationshipRecord) -> None: ...

    @abstractmethod
    def neighbors(self, node_id: str) -> list[dict[str, Any]]: ...


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, vector_id: str, vector: list[float],
               metadata: dict[str, Any]) -> None: ...

    @abstractmethod
    def search(self, vector: list[float],
               limit: int = 10) -> list[dict[str, Any]]: ...


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, document: DocumentRecord) -> DocumentRecord: ...


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...


class MemoryStore(ABC):
    @abstractmethod
    def save(self, memory: MemoryRecord) -> None: ...

    @abstractmethod
    def recall(self, query: str, limit: int = 10) -> list[MemoryRecord]: ...


class Extractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> dict[str, Any]: ...


class Reasoner(ABC):
    @abstractmethod
    def reason(self, query: str, evidence: list[str]) -> dict[str, Any]: ...


class Indexer(ABC):
    @abstractmethod
    def index(self, target_id: str, text: str) -> dict[str, Any]: ...


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]: ...


class KnowledgeSink(ABC):
    """Consumes knowledge to feed AI agents."""
    @abstractmethod
    def receive(self, context: dict[str, Any]) -> None: ...
