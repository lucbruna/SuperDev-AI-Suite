from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from .knowledge_models import KnowledgeEntry, ResearchQuery, ResearchResult, ValidationResult
from .knowledge_interfaces import (
    IKnowledgeSource, IKnowledgeProcessor,
    IKnowledgeStorage, IKnowledgeValidator,
    ConcreteKnowledgeSource, ConcreteKnowledgeProcessor,
    ConcreteKnowledgeStorage, ConcreteKnowledgeValidator,
)

logger = logging.getLogger(__name__)


class KnowledgeProtocol:
    def __init__(self, source: Optional[IKnowledgeSource] = None,
                 processor: Optional[IKnowledgeProcessor] = None,
                 storage: Optional[IKnowledgeStorage] = None,
                 validator: Optional[IKnowledgeValidator] = None):
        self.source = source or ConcreteKnowledgeSource()
        self.processor = processor or ConcreteKnowledgeProcessor()
        self.storage = storage or ConcreteKnowledgeStorage()
        self.validator = validator or ConcreteKnowledgeValidator()

    async def execute(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        validated = await self.validator.validate(entry)
        if not validated.valid:
            logger.warning(f"Entry {entry.id} failed validation")
            return entry
        processed = await self.processor.process(entry)
        await self.storage.store(processed)
        return processed


class ResearchProtocol:
    def __init__(self, source: Optional[IKnowledgeSource] = None,
                 validator: Optional[IKnowledgeValidator] = None):
        self.source = source or ConcreteKnowledgeSource()
        self.validator = validator or ConcreteKnowledgeValidator()

    async def execute(self, query: ResearchQuery) -> ResearchResult:
        findings = await self.source.search(query)
        entries = []
        for f in findings[:query.max_sources]:
            entry = await self.source.fetch(f.get("id", ""))
            if entry:
                entries.append(entry)
        return ResearchResult(
            id=f"res-{query.id}",
            query_id=query.id,
            query=query.query,
            findings=findings,
        )


class LearningProtocol:
    def __init__(self, processor: Optional[IKnowledgeProcessor] = None,
                 storage: Optional[IKnowledgeStorage] = None):
        self.processor = processor or ConcreteKnowledgeProcessor()
        self.storage = storage or ConcreteKnowledgeStorage()

    async def execute(self, feedback: Dict[str, Any]) -> bool:
        entry_id = feedback.get("entry_id", "")
        entry = await self.storage.retrieve(entry_id)
        if not entry:
            return False
        enriched = await self.processor.enrich(entry)
        await self.storage.store(enriched)
        return True


class ValidationProtocol:
    def __init__(self, validator: Optional[IKnowledgeValidator] = None):
        self.validator = validator or ConcreteKnowledgeValidator()

    async def execute(self, entry: KnowledgeEntry) -> ValidationResult:
        return await self.validator.validate(entry)


class IntegrationProtocol:
    def __init__(self, source: Optional[IKnowledgeSource] = None,
                 processor: Optional[IKnowledgeProcessor] = None,
                 storage: Optional[IKnowledgeStorage] = None,
                 validator: Optional[IKnowledgeValidator] = None):
        self.protocols = {
            "knowledge": KnowledgeProtocol(source, processor, storage, validator),
            "research": ResearchProtocol(source, validator),
            "learning": LearningProtocol(processor, storage),
            "validation": ValidationProtocol(validator),
        }

    def get_protocol(self, name: str):
        return self.protocols.get(name)