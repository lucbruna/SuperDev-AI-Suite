"""Knowledge Engine Configuration."""
from dataclasses import dataclass, field


@dataclass
class KnowledgeConfig:
    embedding_model: str = "default"
    embedding_dimensions: int = 384
    vector_db_path: str = "./vector_db"
    max_query_results: int = 10
    confidence_threshold: float = 0.7
    validation_enabled: bool = True
    learning_enabled: bool = True
    max_document_size_mb: int = 50
    chunk_size: int = 512
    chunk_overlap: int = 50
    research_sources: list[str] = field(default_factory=lambda: ["web", "documents", "database"])
    cache_ttl_seconds: int = 3600
    max_concurrent_research: int = 5
    knowledge_graph_enabled: bool = True
    auto_validate: bool = True
    retention_days: int = 365
    metrics_enabled: bool = True
    log_level: str = "info"
