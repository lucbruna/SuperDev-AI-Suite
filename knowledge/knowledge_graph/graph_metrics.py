from __future__ import annotations

import logging
from typing import Any

from .graph import KnowledgeGraph


class GraphMetrics:
    """Computes structural metrics for the knowledge graph."""

    def __init__(self, graph: KnowledgeGraph | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.graph_metrics")
        self.graph = graph or KnowledgeGraph()

    def degrees(self) -> dict[str, int]:
        degrees: dict[str, int] = {}
        for relation in self.graph.relations():
            degrees[relation.source] = degrees.get(relation.source, 0) + 1
            degrees[relation.target] = degrees.get(relation.target, 0) + 1
        return degrees

    def most_connected(self, limit: int = 5) -> list[tuple[str, int]]:
        return sorted(self.degrees().items(), key=lambda pair: pair[1], reverse=True)[:limit]

    def isolated(self) -> list[str]:
        degrees = self.degrees()
        return [entity.name for entity in self.graph.entities() if degrees.get(entity.name, 0) == 0]

    def density(self) -> float:
        entity_count = len(self.graph.entities())
        if entity_count < 2:
            return 0.0
        max_possible = entity_count * (entity_count - 1) / 2
        return len(self.graph.relations()) / max_possible
