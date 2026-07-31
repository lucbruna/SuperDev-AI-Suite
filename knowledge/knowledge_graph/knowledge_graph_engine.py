from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import Entity, Relation
from .entity_extractor import EntityExtractor
from .graph import KnowledgeGraph
from .graph_builder import GraphBuilder
from .graph_metrics import GraphMetrics
from .graph_search import GraphSearch
from .graph_traversal import GraphTraversal
from .relation_extractor import RelationExtractor


class KnowledgeGraphEngine:
    """Composes graph building, search, traversal, and metrics."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.graph = KnowledgeGraph()
        self.builder = GraphBuilder(EntityExtractor(), RelationExtractor())
        self.search = GraphSearch(self.graph)
        self.traversal = GraphTraversal(self.graph)
        self.metrics_calculator = GraphMetrics(self.graph)

    def add_text(self, text: str) -> None:
        self.builder.build_from_text(text, self.graph)
        self.metrics.increment("knowledge_graph.texts")
        self.events.emit(KnowledgeEventType.GRAPH_UPDATED, {"entities": len(self.graph.entities())})

    def add_entity(self, entity: Entity) -> None:
        self.graph.add_entity(entity)

    def add_relation(self, relation: Relation) -> None:
        self.graph.add_relation(relation)

    def related(self, entity_name: str) -> list[str]:
        return self.graph.neighbors(entity_name)

    def path(self, start: str, target: str) -> list[str]:
        return self.search.shortest_path(start, target)

    def stats(self) -> dict[str, Any]:
        return {
            **self.graph.count(),
            "density": self.metrics_calculator.density(),
            "isolated": len(self.metrics_calculator.isolated()),
            "most_connected": self.metrics_calculator.most_connected(3),
        }
