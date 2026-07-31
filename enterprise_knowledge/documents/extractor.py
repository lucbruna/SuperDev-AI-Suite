"""Entity/relation extraction from document text."""

from __future__ import annotations

import re
from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize
from enterprise_knowledge.knowledge_models import NodeType, RelationshipType

_PERSON_RE = re.compile(r"\b([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,2})\b")
_ACRONYM_RE = re.compile(r"\b([A-Z]{2,6})\b")

_KNOWN_TYPES = {
    "cliente": NodeType.PERSON, "pessoa": NodeType.PERSON,
    "projeto": NodeType.PROJECT, "código": NodeType.CODE,
    "decisão": NodeType.DECISION, "documento": NodeType.DOCUMENT,
    "solução": NodeType.SOLUTION, "problema": NodeType.PROBLEM,
    "sistema": NodeType.SYSTEM, "empresa": NodeType.COMPANY,
    "banco": NodeType.DATABASE, "equipe": NodeType.TEAM,
    "agente": NodeType.AGENT, "contrato": NodeType.CONTRACT,
}

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


class EntityExtractor:
    """Extracts entities and typed relations from text."""

    def __init__(self) -> None:
        self.known_types = dict(_KNOWN_TYPES)
        self.relation_verbs = dict(_RELATION_VERBS)

    def extract(self, text: str) -> dict[str, list[dict[str, Any]]]:
        return {"entities": self.extract_entities(text),
                "relations": self.extract_relations(text)}

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        seen: set[str] = set()
        for match in _PERSON_RE.finditer(text):
            name = match.group(1)
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            entities.append({"name": name, "type": "person"})
        for match in _ACRONYM_RE.finditer(text):
            acronym = match.group(1)
            if acronym.lower() in seen or acronym in ("I", "II"):
                continue
            seen.add(acronym.lower())
            entities.append({"name": acronym, "type": "acronym"})
        return entities

    def extract_relations(self, text: str) -> list[dict[str, Any]]:
        relations: list[dict[str, Any]] = []
        sentences = re.split(r"[.!?]\s+", text)
        for sentence in sentences:
            words = tokenize(sentence.lower())
            for word in words:
                rel_type = self.relation_verbs.get(word)
                if rel_type is not None:
                    relations.append({"sentence": sentence.strip(),
                                      "verb": word,
                                      "type": rel_type.value})
                    break
        return relations

    def classify_entity(self, token: str) -> NodeType:
        return self.known_types.get(token.lower(), NodeType.CONCEPT)
