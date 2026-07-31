from __future__ import annotations

from typing import Any

from .concepts import Concept
from .relationships import Relationship


class Ontology:
    """Formal ontology defining concepts and their relationships."""

    def __init__(self, name: str = ""):
        self._name = name
        self._concepts: dict[str, Concept] = {}
        self._relationships: dict[str, Relationship] = {}
        self._axioms: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def concepts(self) -> dict[str, Concept]:
        return dict(self._concepts)

    @property
    def relationships(self) -> dict[str, Relationship]:
        return dict(self._relationships)

    def add_concept(self, concept: Concept) -> None:
        self._concepts[concept.name] = concept

    def get_concept(self, name: str) -> Concept | None:
        return self._concepts.get(name)

    def remove_concept(self, name: str) -> bool:
        return self._concepts.pop(name, None) is not None

    def add_relationship(self, relationship: Relationship) -> None:
        self._relationships[relationship.name] = relationship

    def get_relationship(self, name: str) -> Relationship | None:
        return self._relationships.get(name)

    def add_axiom(self, axiom: dict[str, Any]) -> None:
        self._axioms.append(axiom)

    def clear(self) -> None:
        self._concepts.clear()
        self._relationships.clear()
        self._axioms.clear()
