from __future__ import annotations

from typing import Any

from .concepts import Concept
from .graph import KnowledgeGraph
from .ontology import Ontology
from .relationships import Relationship
from .semantic_network import SemanticNetwork
from .taxonomy import Taxonomy


class KnowledgeValidator:
    """Validation and consistency checking for knowledge structures."""

    def __init__(self):
        self._errors: list[str] = []
        self._warnings: list[str] = []

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    @property
    def warnings(self) -> list[str]:
        return list(self._warnings)

    def validate_ontology(self, ontology: Ontology) -> dict[str, Any]:
        self._errors.clear()
        self._warnings.clear()
        seen_concepts: set[str] = set()
        for name, concept in ontology.concepts.items():
            if name in seen_concepts:
                self._warnings.append(f"Duplicate concept definition: {name}")
            seen_concepts.add(name)
            self._validate_concept(concept)
        seen_rels: set[str] = set()
        for name, rel in ontology.relationships.items():
            if name in seen_rels:
                self._warnings.append(f"Duplicate relationship definition: {name}")
            seen_rels.add(name)
            self._validate_relationship(rel, ontology)
        return {
            "valid": len(self._errors) == 0,
            "errors": list(self._errors),
            "warnings": list(self._warnings),
        }

    def _validate_concept(self, concept: Concept) -> None:
        if not concept.name:
            self._errors.append("Concept must have a non-empty name")

    def _validate_relationship(self, rel: Relationship, ontology: Ontology) -> None:
        if rel.source not in ontology.concepts:
            self._errors.append(f"Relationship {rel.name} references unknown source concept: {rel.source}")
        if rel.target not in ontology.concepts:
            self._errors.append(f"Relationship {rel.name} references unknown target concept: {rel.target}")

    def validate_graph(self, graph: KnowledgeGraph) -> dict[str, Any]:
        self._errors.clear()
        self._warnings.clear()
        for e in graph.edges:
            if e["source"] not in graph.nodes:
                self._errors.append(f"Edge references unknown source node: {e['source']}")
            if e["target"] not in graph.nodes:
                self._errors.append(f"Edge references unknown target node: {e['target']}")
        return {
            "valid": len(self._errors) == 0,
            "errors": list(self._errors),
            "warnings": list(self._warnings),
        }

    def validate_network(self, network: SemanticNetwork) -> dict[str, Any]:
        return self.validate_graph(network.graph)

    def validate_taxonomy(self, taxonomy: Taxonomy) -> dict[str, Any]:
        self._errors.clear()
        self._warnings.clear()
        for node in taxonomy.nodes.values():
            if node.parent and node.parent not in taxonomy.nodes:
                self._errors.append(f"Node {node.name} references unknown parent: {node.parent}")
        return {
            "valid": len(self._errors) == 0,
            "errors": list(self._errors),
            "warnings": list(self._warnings),
        }

    def check_consistency(self, ontology: Ontology, network: SemanticNetwork) -> dict[str, Any]:
        self._errors.clear()
        self._warnings.clear()
        for concept_name in ontology.concepts:
            if network.get_concept(concept_name) is None:
                self._warnings.append(f"Concept {concept_name} defined in ontology but missing from network")
        for node_id in network.graph.nodes:
            if node_id not in ontology.concepts:
                self._warnings.append(f"Node {node_id} in network but not defined in ontology")
        return {
            "valid": len(self._errors) == 0,
            "errors": list(self._errors),
            "warnings": list(self._warnings),
        }

    def clear(self) -> None:
        self._errors.clear()
        self._warnings.clear()
