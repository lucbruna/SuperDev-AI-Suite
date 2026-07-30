from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .knowledge_index import KnowledgeIndex
from .ontology import Ontology
from .semantic_network import SemanticNetwork


class KnowledgeRepository:
    """Storage and retrieval layer for knowledge artefacts."""

    def __init__(
        self,
        ontology: Ontology | None = None,
        network: SemanticNetwork | None = None,
        index: KnowledgeIndex | None = None,
    ):
        self._ontology = ontology or Ontology()
        self._network = network or SemanticNetwork()
        self._index = index or KnowledgeIndex()

    @property
    def ontology(self) -> Ontology:
        return self._ontology

    @property
    def network(self) -> SemanticNetwork:
        return self._network

    @property
    def index(self) -> KnowledgeIndex:
        return self._index

    def store(self, key: str, data: dict[str, Any]) -> None:
        self._index.add_entry(key, data)

    def retrieve(self, key: str) -> dict[str, Any] | None:
        return self._index.get_entry(key)

    def delete(self, key: str) -> bool:
        return self._index.remove_entry(key)

    def search(self, query: str) -> list[dict[str, Any]]:
        return self._index.search(query)

    def save_to_disk(self, path: str | Path) -> None:
        data = {
            "ontology": self._ontology.to_dict(),
            "network": self._network.to_dict(),
            "index": self._index.to_dict(),
        }
        Path(path).write_text(json.dumps(data, indent=2))

    def load_from_disk(self, path: str | Path) -> None:
        data = json.loads(Path(path).read_text())
        self._ontology = Ontology.from_dict(data.get("ontology", {}))
        self._network = SemanticNetwork.from_dict(data.get("network", {}))
        self._index = KnowledgeIndex.from_dict(data.get("index", {}))

    def clear(self) -> None:
        self._ontology.clear()
        self._network.clear()
        self._index.clear()
