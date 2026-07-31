from __future__ import annotations

import logging

from ..knowledge_models import Entity, Relation
from .entity_extractor import EntityExtractor
from .graph import KnowledgeGraph
from .relation_extractor import RelationExtractor


class GraphBuilder:
    """Builds a knowledge graph from documents or raw text."""

    def __init__(
        self,
        entity_extractor: EntityExtractor | None = None,
        relation_extractor: RelationExtractor | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.graph_builder")
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.relation_extractor = relation_extractor or RelationExtractor()

    def build_from_text(self, text: str, graph: KnowledgeGraph | None = None) -> KnowledgeGraph:
        graph = graph or KnowledgeGraph()
        entities = self.entity_extractor.extract(text)
        for entity in entities:
            graph.add_entity(entity)
        relations = self.relation_extractor.extract(text, entities)
        for relation in relations:
            graph.add_relation(relation)
        return graph

    def build_from_documents(self, documents: list, graph: KnowledgeGraph | None = None) -> KnowledgeGraph:
        graph = graph or KnowledgeGraph()
        for document in documents:
            content = getattr(document, "content", "")
            self.build_from_text(content, graph)
        return graph
