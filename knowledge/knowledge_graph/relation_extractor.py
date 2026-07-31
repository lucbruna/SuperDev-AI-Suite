from __future__ import annotations

import logging
import re

from ..knowledge_models import Entity, Relation


class RelationExtractor:
    """Infers co-occurrence relations between entities in the same sentence."""

    def __init__(self, default_relation: str = "co_occurs_with") -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.relation_extractor")
        self._default_relation = default_relation

    def extract(self, text: str, entities: list[Entity]) -> list[Relation]:
        name_map = {entity.name.lower(): entity.name for entity in entities}
        lowered = text.lower()
        sentences = re.split(r"[.!?;]\s+", lowered or "")
        relations: list[Relation] = []
        for sentence in sentences:
            present = [name_map[name] for name in name_map if name in sentence]
            for i, source in enumerate(present):
                for target in present[i + 1:]:
                    relations.append(
                        Relation(source=source, target=target, relation_type=self._default_relation)
                    )
        return relations
