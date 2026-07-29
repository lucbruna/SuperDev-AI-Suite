from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceInfo:
    id: str
    name: str
    category: str
    base_url: str
    quality_score: float = 0.8
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


PREDEFINED_SOURCES: list[SourceInfo] = [
    SourceInfo(id="src_web_001", name="Google Scholar", category="academic", base_url="https://scholar.google.com", quality_score=0.85, metadata={"type": "search_engine", "rate_limit": 10}),
    SourceInfo(id="src_web_002", name="ArXiv", category="academic", base_url="https://arxiv.org", quality_score=0.9, metadata={"type": "preprint_repository", "fields": ["cs", "math", "physics"]}),
    SourceInfo(id="src_web_003", name="Wikipedia", category="web", base_url="https://en.wikipedia.org", quality_score=0.75, metadata={"type": "encyclopedia", "languages": 300}),
    SourceInfo(id="src_web_004", name="GitHub", category="technical", base_url="https://github.com", quality_score=0.8, metadata={"type": "code_repository"}),
    SourceInfo(id="src_web_005", name="Stack Overflow", category="technical", base_url="https://stackoverflow.com", quality_score=0.78, metadata={"type": "qa_forum"}),
    SourceInfo(id="src_web_006", name="IEEE Xplore", category="academic", base_url="https://ieeexplore.ieee.org", quality_score=0.92, metadata={"type": "digital_library", "subscription_required": True}),
    SourceInfo(id="src_web_007", name="Internal Wiki", category="internal", base_url="https://internal.company.com/wiki", quality_score=0.7, metadata={"type": "internal_knowledge_base"}),
    SourceInfo(id="src_web_008", name="News API", category="web", base_url="https://newsapi.org", quality_score=0.65, metadata={"type": "news_aggregator"}),
    SourceInfo(id="src_web_009", name="PubMed", category="academic", base_url="https://pubmed.ncbi.nlm.nih.gov", quality_score=0.95, metadata={"type": "medical_database"}),
    SourceInfo(id="src_web_010", name="Medium", category="web", base_url="https://medium.com", quality_score=0.6, metadata={"type": "blogging_platform"}),
]


class SourceManager:
    def __init__(self) -> None:
        self._sources: dict[str, SourceInfo] = {s.id: s for s in PREDEFINED_SOURCES}

    def register_source(self, source: SourceInfo) -> str:
        if source.id in self._sources:
            raise ValueError(f"Source with id '{source.id}' already exists")
        self._sources[source.id] = source
        return source.id

    def list_sources(self, category: str | None = None) -> list[SourceInfo]:
        if category:
            return [s for s in self._sources.values() if s.category == category and s.is_active]
        return [s for s in self._sources.values() if s.is_active]

    def validate_source(self, source_id: str) -> bool:
        source = self._sources.get(source_id)
        if source is None:
            return False
        return source.is_active and source.quality_score >= 0.5

    def get_source_quality(self, source_id: str) -> float:
        source = self._sources.get(source_id)
        if source is None:
            raise KeyError(f"Source '{source_id}' not found")
        return source.quality_score

    def categorize_source(self, source_id: str) -> str:
        source = self._sources.get(source_id)
        if source is None:
            raise KeyError(f"Source '{source_id}' not found")
        return source.category