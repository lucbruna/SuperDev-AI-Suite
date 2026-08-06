"""Graph configuration — node/edge model and build behaviour.

Controls how the knowledge graph is assembled from scan results.
Environment prefix: ``SUPERDEV_KG_GRAPH_*``.
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
class GraphConfig:
    """Configuration for the knowledge graph builder."""

    max_nodes: int = 200_000
    max_edges: int = 500_000
    merge_duplicate_edges: bool = True
    validate_on_build: bool = True
    index_contains_edges: bool = True
    track_lineage: bool = True
    include_docstrings: bool = True
    include_comments: bool = False
    layering: bool = True

    # Edge weights for relation scoring (0..1).
    import_weight: float = 1.0
    call_weight: float = 0.9
    inherit_weight: float = 0.8
    semantic_weight: float = 0.5

    @classmethod
    def from_env(cls) -> "GraphConfig":
        cfg = cls()
        cfg.max_nodes = int(os.getenv("SUPERDEV_KG_GRAPH_MAX_NODES", str(cfg.max_nodes)))
        cfg.max_edges = int(os.getenv("SUPERDEV_KG_GRAPH_MAX_EDGES", str(cfg.max_edges)))
        cfg.validate_on_build = _env_bool("SUPERDEV_KG_GRAPH_VALIDATE", cfg.validate_on_build)
        cfg.include_docstrings = _env_bool("SUPERDEV_KG_GRAPH_DOCSTRINGS", cfg.include_docstrings)
        return cfg
