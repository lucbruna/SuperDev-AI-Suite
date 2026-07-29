from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .knowledge_models import (
    KnowledgeEntry, ResearchQuery, ResearchResult,
    DocumentAnalysis, ValidationResult, EmbeddingVector,
)

logger = logging.getLogger(__name__)


class IKnowledgeSource(ABC):
    @abstractmethod
    async def search(self, query: ResearchQuery) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def fetch(self, source_id: str) -> Optional[KnowledgeEntry]: ...

    @abstractmethod
    async def validate(self, source_id: str) -> Dict[str, Any]: ...


class IKnowledgeProcessor(ABC):
    @abstractmethod
    async def process(self, entry: KnowledgeEntry) -> KnowledgeEntry: ...

    @abstractmethod
    async def analyze(self, entry: KnowledgeEntry) -> Dict[str, Any]: ...

    @abstractmethod
    async def enrich(self, entry: KnowledgeEntry) -> KnowledgeEntry: ...


class IKnowledgeStorage(ABC):
    @abstractmethod
    async def store(self, entry: KnowledgeEntry) -> str: ...

    @abstractmethod
    async def retrieve(self, entry_id: str) -> Optional[KnowledgeEntry]: ...

    @abstractmethod
    async def delete(self, entry_id: str) -> bool: ...

    @abstractmethod
    async def query(self, query: str, limit: int = 10) -> List[KnowledgeEntry]: ...


class IKnowledgeValidator(ABC):
    @abstractmethod
    async def validate(self, entry: KnowledgeEntry) -> ValidationResult: ...

    @abstractmethod
    async def verify(self, entry: KnowledgeEntry) -> bool: ...

    @abstractmethod
    async def score(self, entry: KnowledgeEntry) -> float: ...


class ConcreteKnowledgeSource(IKnowledgeSource):
    async def search(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        logger.info(f"Searching for: {query.query}")
        return []

    async def fetch(self, source_id: str) -> Optional[KnowledgeEntry]:
        logger.info(f"Fetching source: {source_id}")
        return None

    async def validate(self, source_id: str) -> Dict[str, Any]:
        return {"valid": True, "source_id": source_id}


class ConcreteKnowledgeProcessor(IKnowledgeProcessor):
    async def process(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        logger.info(f"Processing entry: {entry.id}")
        return entry

    async def analyze(self, entry: KnowledgeEntry) -> Dict[str, Any]:
        return {"entry_id": entry.id, "word_count": len(entry.content.split())}

    async def enrich(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        logger.info(f"Enriching entry: {entry.id}")
        return entry


class ConcreteKnowledgeStorage(IKnowledgeStorage):
    def __init__(self):
        self._store: Dict[str, KnowledgeEntry] = {}

    async def store(self, entry: KnowledgeEntry) -> str:
        self._store[entry.id] = entry
        return entry.id

    async def retrieve(self, entry_id: str) -> Optional[KnowledgeEntry]:
        return self._store.get(entry_id)

    async def delete(self, entry_id: str) -> bool:
        if entry_id in self._store:
            del self._store[entry_id]
            return True
        return False

    async def query(self, query: str, limit: int = 10) -> List[KnowledgeEntry]:
        results = [e for e in self._store.values() if query.lower() in e.title.lower() or query.lower() in e.content.lower()]
        return results[:limit]


class ConcreteKnowledgeValidator(IKnowledgeValidator):
    async def validate(self, entry: KnowledgeEntry) -> ValidationResult:
        checks_passed = []
        checks_failed = []
        if entry.content:
            checks_passed.append("has_content")
        else:
            checks_failed.append("no_content")
        if entry.source:
            checks_passed.append("has_source")
        else:
            checks_failed.append("no_source")
        valid = len(checks_failed) == 0
        return ValidationResult(
            id=f"val-{entry.id}",
            entry_id=entry.id,
            valid=valid,
            confidence=0.8 if valid else 0.0,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            validator="concrete",
        )

    async def verify(self, entry: KnowledgeEntry) -> bool:
        return bool(entry.content and entry.source)

    async def score(self, entry: KnowledgeEntry) -> float:
        score = 0.5
        if entry.content:
            score += 0.2
        if entry.source:
            score += 0.2
        return min(score, 1.0)