"""Semantic configuration — similarity, ontology and semantic linking.

Environment prefix: ``SUPERDEV_KG_SEM_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class SemanticConfig:
    """Configuration for the semantic engine."""

    enabled: bool = True
    similarity_threshold: float = 0.75
    link_similar_entities: bool = True
    max_similar_links_per_entity: int = 8
    build_ontology: bool = True
    concept_map_enabled: bool = True
    meaning_extraction: bool = True
    language: str = "en"

    @classmethod
    def from_env(cls) -> "SemanticConfig":
        cfg = cls()
        cfg.enabled = _env_bool("SUPERDEV_KG_SEM_ENABLED", cfg.enabled)
        cfg.similarity_threshold = float(
            os.getenv("SUPERDEV_KG_SEM_THRESHOLD", str(cfg.similarity_threshold))
        )
        cfg.build_ontology = _env_bool("SUPERDEV_KG_SEM_ONTOLOGY", cfg.build_ontology)
        return cfg
