"""Knowledge Engine Interfaces — Abstract interfaces for the knowledge platform."""

from abc import ABC, abstractmethod
from typing import Any

from .knowledge_models import ConfidenceLevel, Document, Knowledge, ResearchQuery, ResearchResult


class ResearchInterface(ABC):
    @abstractmethod
    def search(self, query: ResearchQuery) -> list[ResearchResult]:
        pass

    @abstractmethod
    def collect(self, source_url: str) -> ResearchResult | None:
        pass

    @abstractmethod
    def plan_research(self, topic: str) -> dict[str, Any]:
        pass


class DocumentInterface(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Document | None:
        pass

    @abstractmethod
    def extract_information(self, document: Document) -> dict[str, Any]:
        pass

    @abstractmethod
    def summarize(self, document: Document) -> str:
        pass


class VectorMemoryInterface(ABC):
    @abstractmethod
    def store(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, vector_id: str) -> bool:
        pass


class EmbeddingInterface(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass

    @abstractmethod
    def batch_embed(self, texts: list[str]) -> list[list[float]]:
        pass

    @abstractmethod
    def similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        pass


class ReasoningInterface(ABC):
    @abstractmethod
    def analyze(self, problem: str, context: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    def hypothesize(self, observations: list[str]) -> list[str]:
        pass

    @abstractmethod
    def conclude(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        pass


class LearningInterface(ABC):
    @abstractmethod
    def record_experience(self, experience: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def analyze_patterns(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def suggest_improvements(self) -> list[str]:
        pass


class ValidationInterface(ABC):
    @abstractmethod
    def validate(self, knowledge: Knowledge) -> ConfidenceLevel:
        pass

    @abstractmethod
    def check_source(self, source_url: str) -> bool:
        pass

    @abstractmethod
    def fact_check(self, statement: str) -> dict[str, Any]:
        pass


class KnowledgeGraphInterface(ABC):
    @abstractmethod
    def add_entity(self, name: str, entity_type: str) -> str:
        pass

    @abstractmethod
    def add_relationship(self, entity_a: str, entity_b: str, relationship: str) -> bool:
        pass

    @abstractmethod
    def query_graph(self, entity: str) -> dict[str, Any]:
        pass
