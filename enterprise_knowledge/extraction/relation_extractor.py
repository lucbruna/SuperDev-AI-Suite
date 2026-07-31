"""Relation extraction between entities found in text."""

from __future__ import annotations

import re
from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize
from enterprise_knowledge.knowledge_models import RelationshipType

_RELATION_VERBS = {
    "usa": RelationshipType.USES, "utiliza": RelationshipType.USES,
    "tem": RelationshipType.HAS, "possui": RelationshipType.HAS,
    "resolve": RelationshipType.RESOLVED_BY,
    "resolvido": RelationshipType.RESOLVED_BY,
    "corrige": RelationshipType.RESOLVED_BY,
    "corrigido": RelationshipType.RESOLVED_BY,
    "implementa": RelationshipType.IMPLEMENTS,
    "depende": RelationshipType.DEPENDS_ON,
    "causa": RelationshipType.CAUSES,
    "documenta": RelationshipType.DOCUMENTS,
    "pertence": RelationshipType.BELONGS_TO,
    "conecta": RelationshipType.CONNECTED_TO,
    "relaciona": RelationshipType.RELATES_TO,
    "decide": RelationshipType.DECIDED_IN,
}


class RelationExtractor:
    """Discovers subject-verb-object triples in sentences."""

    def __init__(self) -> None:
        self.verbs = dict(_RELATION_VERBS)

    def extract(self, text: str) -> list[dict[str, Any]]:
        relations = []
        sentences = re.split(r"[.!?]\s+", text or "")
        for sentence in sentences:
            words = tokenize(sentence)
            for index, word in enumerate(words):
                rel_type = self.verbs.get(word)
                if rel_type is None:
                    continue
                subject = self._subject(words[:index])
                target = self._target(words[index + 1:])
                if not subject and not target:
                    continue
                relations.append({
                    "subject": subject, "verb": word,
                    "target": target,
                    "type": rel_type.value,
                    "sentence": sentence.strip(),
                })
                break
        return relations

    @staticmethod
    def _subject(words: list[str]) -> str:
        return " ".join(words[-2:]) if words else ""

    @staticmethod
    def _target(words: list[str]) -> str:
        return " ".join(words[:2]) if words else ""
