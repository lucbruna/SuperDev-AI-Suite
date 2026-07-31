from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable

from .knowledge_models import DocumentRecord, SearchResult


@runtime_checkable
class Retriever(Protocol):
    """Protocol for anything that retrieves context for a query."""

    def retrieve(self, query: str, top_k: int = 5) -> list[SearchResult]: ...


@runtime_checkable
class Classifier(Protocol):
    """Protocol for content classifiers."""

    def classify(self, text: str) -> str: ...


@runtime_checkable
class Summarizer(Protocol):
    """Protocol for text summarizers."""

    def summarize(self, text: str, max_length: int = 200) -> str: ...


@runtime_checkable
class DocumentProcessor(Protocol):
    """Protocol for format-specific document processors."""

    def can_handle(self, path: str) -> bool: ...

    def parse(self, path: str) -> DocumentRecord: ...


@runtime_checkable
class Loader(Protocol):
    """Protocol for knowledge ingestion loaders."""

    def load(self, source: str) -> list[str]: ...


@runtime_checkable
class GraphQuery(Protocol):
    """Protocol for knowledge graph queries."""

    def query(self, query: str) -> list[dict[str, Any]]: ...


@runtime_checkable
class Rule(Protocol):
    """Protocol for inference rules."""

    def applies(self, context: dict[str, Any]) -> bool: ...

    def apply(self, context: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class Hook(Protocol):
    """Protocol for engine lifecycle hooks."""

    def __call__(self, event_type: str, payload: dict[str, Any]) -> None: ...


Callback = Callable[..., Any]
