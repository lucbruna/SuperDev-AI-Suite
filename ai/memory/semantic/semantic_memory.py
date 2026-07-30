from __future__ import annotations

from typing import Any, Dict, List, Optional

from .concepts import Concept
from .entities import Entity
from .knowledge_loader import KnowledgeLoader
from .ontology import Ontology
from .relationships import Relationship
from .semantic_index import SemanticIndex
from .semantic_links import SemanticLink
from .semantic_search import SemanticSearch
from .taxonomy import Taxonomy


class SemanticMemory:
    """High-level facade for semantic memory — acquired knowledge."""

    def __init__(self):
        self._concepts: Dict[str, Concept] = {}
        self._entities: Dict[str, Entity] = {}
        self._ontology = Ontology()
        self._taxonomy = Taxonomy()
        self._links: List[SemanticLink] = []
        self._relationships: Dict[str, Relationship] = {}
        self._search = SemanticSearch()
        self._index = SemanticIndex()
        self._loader = KnowledgeLoader()

    @property
    def ontology(self) -> Ontology:
        return self._ontology

    @property
    def taxonomy(self) -> Taxonomy:
        return self._taxonomy

    @property
    def search(self) -> SemanticSearch:
        return self._search

    @property
    def index(self) -> SemanticIndex:
        return self._index

    @property
    def loader(self) -> KnowledgeLoader:
        return self._loader

    def add_concept(self, concept: Concept) -> None:
        self._concepts[concept.name] = concept
        self._index.index_concept(concept)

    def get_concept(self, name: str) -> Concept | None:
        return self._concepts.get(name)

    def add_entity(self, entity: Entity) -> None:
        self._entities[entity.entity_id] = entity
        self._index.index_entity(entity)

    def get_entity(self, entity_id: str) -> Entity | None:
        return self._entities.get(entity_id)

    def add_relationship(self, relationship: Relationship) -> None:
        self._relationships[relationship.name] = relationship

    def add_link(self, link: SemanticLink) -> None:
        self._links.append(link)

    def query(self, query: str) -> List[Dict[str, Any]]:
        return self._search.search(query, self._concepts, self._entities, self._links)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "concepts": len(self._concepts),
            "entities": len(self._entities),
            "relationships": len(self._relationships),
            "links": len(self._links),
            "ontology_size": len(self._ontology.concepts),
        }
