from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeConfig:
    """Configuration for the Knowledge & Memory Engine."""

    workspace_id: str = "default"
    memory_limit: int = 10000
    short_term_limit: int = 100
    embedding_dimensions: int = 384
    embedding_model: str = "local-hash"
    vector_store_backend: str = "in-memory"
    chunk_size: int = 512
    chunk_overlap: int = 64
    rag_top_k: int = 5
    similarity_threshold: float = 0.5
    enable_governance: bool = True
    retention_days: int = 365
    storage_path: str = ".knowledge"
    extra: dict[str, Any] = field(default_factory=dict)

    def merge(self, overrides: dict[str, Any]) -> KnowledgeConfig:
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra[key] = value
        return self
