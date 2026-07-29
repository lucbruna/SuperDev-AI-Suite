from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ResearchConfig:
    max_sources: int = 50
    search_depth: str = "comprehensive"
    enable_web_search: bool = True
    enable_cross_reference: bool = True
    enable_fact_checking: bool = True
    timeout_seconds: int = 60
    max_iterations: int = 3


@dataclass
class DocumentConfig:
    max_pages: int = 200
    ocr_enabled: bool = True
    enable_summarization: bool = True
    enable_entity_extraction: bool = True
    enable_qa: bool = True
    supported_formats: List[str] = field(default_factory=lambda: ["pdf", "docx", "txt", "md", "html", "csv", "json", "xml"])
    max_file_size_mb: float = 100.0


@dataclass
class VectorMemoryConfig:
    dimension: int = 768
    index_type: str = "hnsw"
    similarity_metric: str = "cosine"
    ef_construction: int = 200
    m_neighbors: int = 16
    enable_cache: bool = True
    cache_size: int = 10000


@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    max_seq_length: int = 512
    normalize_embeddings: bool = True
    enable_gpu: bool = False
    cache_embeddings: bool = True


@dataclass
class ReasoningConfig:
    max_hypotheses: int = 10
    confidence_threshold: float = 0.7
    enable_abductive: bool = True
    enable_deductive: bool = True
    enable_inductive: bool = True
    max_reasoning_depth: int = 5
    enable_contradiction_check: bool = True


@dataclass
class LearningConfig:
    feedback_window_days: int = 30
    auto_improve: bool = True
    enable_reinforcement: bool = True
    min_feedback_samples: int = 10
    learning_rate: float = 0.01
    enable_pattern_discovery: bool = True


@dataclass
class ValidationConfig:
    min_confidence: float = 0.6
    require_source: bool = True
    enable_cross_validation: bool = True
    max_validation_attempts: int = 3
    staleness_days: int = 365
    enable_peer_review: bool = False


@dataclass
class KnowledgeGraphConfig:
    max_depth: int = 10
    auto_relation: bool = True
    enable_inference: bool = True
    max_nodes: int = 1000000
    relation_confidence_threshold: float = 0.5
    enable_cycle_detection: bool = True


@dataclass
class KnowledgeConfig:
    engine_name: str = "KnowledgeAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    enable_auto_sync: bool = True
    max_concurrent_operations: int = 50
    research: ResearchConfig = field(default_factory=ResearchConfig)
    documents: DocumentConfig = field(default_factory=DocumentConfig)
    vector_memory: VectorMemoryConfig = field(default_factory=VectorMemoryConfig)
    embeddings: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    reasoning: ReasoningConfig = field(default_factory=ReasoningConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    knowledge_graph: KnowledgeGraphConfig = field(default_factory=KnowledgeGraphConfig)
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KnowledgeConfig:
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    sub = getattr(config, key)
                    if hasattr(sub, "__dataclass_fields__"):
                        for sk, sv in value.items():
                            if hasattr(sub, sk):
                                setattr(sub, sk, sv)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config

    @classmethod
    def from_json(cls, path: str) -> KnowledgeConfig:
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def validate(self) -> List[str]:
        errors = []
        if self.research.max_sources < 1:
            errors.append("research.max_sources must be positive")
        if self.vector_memory.dimension < 1:
            errors.append("vector_memory.dimension must be positive")
        if self.reasoning.confidence_threshold < 0 or self.reasoning.confidence_threshold > 1:
            errors.append("reasoning.confidence_threshold must be between 0 and 1")
        if self.validation.min_confidence < 0 or self.validation.min_confidence > 1:
            errors.append("validation.min_confidence must be between 0 and 1")
        if self.knowledge_graph.max_depth < 1:
            errors.append("knowledge_graph.max_depth must be positive")
        if self.documents.max_pages < 1:
            errors.append("documents.max_pages must be at least 1")
        return errors