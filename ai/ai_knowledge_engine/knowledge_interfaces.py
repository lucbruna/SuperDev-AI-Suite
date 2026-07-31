"""Knowledge Engine Interfaces — Abstract interfaces for the knowledge platform."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .knowledge_models import Knowledge, Document, ResearchQuery, ResearchResult, ConfidenceLevel


class ResearchInterface(ABC):
    @abstractmethod
    def search(self, query: ResearchQuery) -> List[ResearchResult]:
        pass

    @abstractmethod
    def collect(self, source_url: str) -> Optional[ResearchResult]:
        pass

    @abstractmethod
    def plan_research(self, topic: str) -> Dict[str, Any]:
        pass


class DocumentInterface(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Optional[Document]:
        pass

    @abstractmethod
    def extract_information(self, document: Document) -> Dict[str, Any]:
        pass

    @abstractmethod
    def summarize(self, document: Document) -> str:
        pass


class VectorMemoryInterface(ABC):
    @abstractmethod
    def store(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, vector_id: str) -> bool:
        pass


class EmbeddingInterface(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        pass


class ReasoningInterface(ABC):
    @abstractmethod
    def analyze(self, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def hypothesize(self, observations: List[str]) -> List[str]:
        pass

    @abstractmethod
    def conclude(self, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass


class LearningInterface(ABC):
    @abstractmethod
    def record_experience(self, experience: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def analyze_patterns(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def suggest_improvements(self) -> List[str]:
        pass


class ValidationInterface(ABC):
    @abstractmethod
    def validate(self, knowledge: Knowledge) -> ConfidenceLevel:
        pass

    @abstractmethod
    def check_source(self, source_url: str) -> bool:
        pass

    @abstractmethod
    def fact_check(self, statement: str) -> Dict[str, Any]:
        pass


class KnowledgeGraphInterface(ABC):
    @abstractmethod
    def add_entity(self, name: str, entity_type: str) -> str:
        pass

    @abstractmethod
    def add_relationship(self, entity_a: str, entity_b: str, relationship: str) -> bool:
        pass

    @abstractmethod
    def query_graph(self, entity: str) -> Dict[str, Any]:
        pass
