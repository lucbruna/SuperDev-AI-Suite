"""Entity extraction from free text."""

from __future__ import annotations

import re
from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize

_PERSON_RE = re.compile(r"\b([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,2})\b")
_ACRONYM_RE = re.compile(r"\b([A-Z]{2,6})\b")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_URL_RE = re.compile(r"https?://[^\s]+")
_DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")

_ENTITY_TYPE_KEYWORDS: dict[str, set[str]] = {
    "project": {"projeto", "sprint", "iniciativa"},
    "database": {"banco", "postgresql", "mysql", "oracle", "sql"},
    "system": {"sistema", "plataforma", "aplicação", "erp"},
    "code": {"módulo", "classe", "função", "script", "api"},
    "decision": {"decisão", "decisão", "escolha"},
    "problem": {"problema", "bug", "erro", "falha", "incidente"},
    "solution": {"solução", "correção", "fix", "workaround"},
}

# Proper nouns recognized directly in text (e.g. "PostgreSQL").
_NAMED_ENTITIES: dict[str, str] = {
    "PostgreSQL": "database", "MySQL": "database", "MongoDB": "database",
    "Oracle": "database", "Redis": "database", "SQL Server": "database",
    "Docker": "system", "Kubernetes": "system", "Kafka": "system",
    "Elasticsearch": "system", "React": "code", "Django": "code",
    "Flask": "code", "FastAPI": "code",
}


class EntityExtractor:
    """Finds named entities and classifies their type."""

    def __init__(self) -> None:
        self.type_keywords = {k: set(v)
                              for k, v in _ENTITY_TYPE_KEYWORDS.items()}
        self.named_entities = dict(_NAMED_ENTITIES)

    def extract(self, text: str) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        seen: set[str] = set()

        def add(name: str, entity_type: str) -> None:
            key = name.lower()
            if key in seen or not name.strip():
                return
            seen.add(key)
            entities.append({"name": name.strip(), "type": entity_type})

        for match in _PERSON_RE.finditer(text):
            add(match.group(1), "person")
        for match in _ACRONYM_RE.finditer(text):
            acronym = match.group(1)
            if acronym not in ("I", "II"):
                add(acronym, "acronym")
        for match in _EMAIL_RE.finditer(text):
            add(match.group(0), "email")
        for match in _URL_RE.finditer(text):
            add(match.group(0), "url")
        for match in _DATE_RE.finditer(text):
            add(match.group(1), "date")
        return entities

    def classify(self, name: str) -> str:
        name_lower = name.lower()
        for entity_type, keywords in self.type_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return entity_type
        return "concept"

    def extract_with_types(self, text: str) -> list[dict[str, Any]]:
        entities = self.extract(text)
        names = {entity["name"].lower() for entity in entities}
        for name, entity_type in self.named_entities.items():
            if name.lower() in names or name.lower() not in \
                    (text or "").lower():
                continue
            entities.append({"name": name, "type": entity_type})
        for entity in entities:
            if entity["type"] in ("person", "email", "url", "date",
                                  "acronym"):
                continue
            entity["type"] = self.classify(entity["name"])
        return entities
