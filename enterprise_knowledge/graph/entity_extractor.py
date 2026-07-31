"""Entity extraction for the Knowledge Graph.

Lightweight, stdlib-only heuristics: named entities (proper nouns),
@-prefixed entities, companies, products and relationships described
with common verbs ("usa", "resolve", "possui"...).
"""

from __future__ import annotations

import re
from typing import Any

from enterprise_knowledge.knowledge_models import (NodeType,
                                                   RelationshipType)
from enterprise_knowledge.knowledge_protocols import tokenize

_PERSON_RE = re.compile(r"\b[A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)*\b")
_ACRONYM_RE = re.compile(r"\b[A-Z]{2,}\b")
_AT_RE = re.compile(r"@([a-zA-Z][\w.-]*)")

_KNOWN_NODE_TYPES = {
    "cliente": NodeType.PERSON,
    "pessoa": NodeType.PERSON,
    "projeto": NodeType.PROJECT,
    "código": NodeType.CODE,
    "decisão": NodeType.DECISION,
    "documento": NodeType.DOCUMENT,
    "solução": NodeType.SOLUTION,
    "problema": NodeType.PROBLEM,
    "sistema": NodeType.SYSTEM,
    "empresa": NodeType.COMPANY,
    "banco": NodeType.DATABASE,
    "equipe": NodeType.TEAM,
    "agente": NodeType.AGENT,
    "contrato": NodeType.CONTRACT,
}

_RELATION_VERBS = {
    "usa": RelationshipType.USES,
    "utiliza": RelationshipType.USES,
    "tem": RelationshipType.HAS,
    "possui": RelationshipType.HAS,
    "resolve": RelationshipType.RESOLVED_BY,
    "resolvido": RelationshipType.RESOLVED_BY,
    "corrige": RelationshipType.RESOLVED_BY,
    "corrigido": RelationshipType.FIXED_IN,
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
    """Extracts entities and typed relations from free text."""

    def __init__(self) -> None:
        self._type_map = dict(_KNOWN_NODE_TYPES)
        self._relation_map = dict(_RELATION_VERBS)

    def register_type(self, keyword: str, node_type: NodeType) -> None:
        self._type_map[keyword.lower()] = node_type

    # -- entities -----------------------------------------------------------
    def entities(self, text: str) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        seen = set()
        words = tokenize(text)
        for word in words:
            if word not in self._type_map:
                continue
            if word in seen:
                continue
            seen.add(word)
            found.append({"name": word,
                          "node_type": self._type_map[word].value})
        # named entities (proper nouns)
        for match in _PERSON_RE.finditer(text or ""):
            name = match.group()
            if name in seen:
                continue
            seen.add(name)
            found.append({"name": name, "node_type": NodeType.CONCEPT.value})
        # acronyms (ERP, SQL, PDF...)
        for match in _ACRONYM_RE.finditer(text or ""):
            name = match.group()
            if name in seen:
                continue
            seen.add(name)
            found.append({"name": name, "node_type": NodeType.CONCEPT.value})
        # @-mentions
        for match in _AT_RE.finditer(text or ""):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            found.append({"name": name, "node_type": NodeType.AGENT.value})
        return found

    # -- relations ----------------------------------------------------------
    def relations(self, text: str) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        words = tokenize(text)
        for index, word in enumerate(words):
            rel_type = self._relation_map.get(word)
            if rel_type is None:
                continue
            source = words[index - 1] if index > 0 else ""
            target = words[index + 1] if index + 1 < len(words) else ""
            if source and target:
                found.append({"source": source, "target": target,
                              "rel_type": rel_type.value,
                              "verb": word})
        return found

    # -- combined -----------------------------------------------------------
    def extract(self, text: str) -> dict[str, Any]:
        return {"entities": self.entities(text),
                "relations": self.relations(text)}
