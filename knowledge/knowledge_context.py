from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeContext:
    """Execution context for a knowledge operation (query, ingestion, retrieval)."""

    workspace_id: str = "default"
    user: str = "anonymous"
    project: str = ""
    query: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def with_attributes(self, **attrs: Any) -> "KnowledgeContext":
        self.attributes.update(attrs)
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "user": self.user,
            "project": self.project,
            "query": self.query,
            "attributes": dict(self.attributes),
        }


@dataclass
class KnowledgeResult:
    """Result envelope returned by knowledge operations."""

    success: bool = True
    data: Any = None
    error: str = ""
    operation: str = ""

    @classmethod
    def ok(cls, operation: str, data: Any = None) -> "KnowledgeResult":
        return cls(success=True, data=data, operation=operation)

    @classmethod
    def fail(cls, operation: str, error: str) -> "KnowledgeResult":
        return cls(success=False, error=error, operation=operation)
