from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntegrationContext:
    """Execution context for an integration operation (connect, invoke, sync)."""

    workspace_id: str = "default"
    user: str = "anonymous"
    connection_id: str = ""
    operation: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def with_attributes(self, **attrs: Any) -> "IntegrationContext":
        self.attributes.update(attrs)
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "user": self.user,
            "connection_id": self.connection_id,
            "operation": self.operation,
            "attributes": dict(self.attributes),
        }


@dataclass
class IntegrationResult:
    """Result envelope returned by integration operations."""

    success: bool = True
    data: Any = None
    error: str = ""
    operation: str = ""

    @classmethod
    def ok(cls, operation: str, data: Any = None) -> "IntegrationResult":
        return cls(success=True, data=data, operation=operation)

    @classmethod
    def fail(cls, operation: str, error: str) -> "IntegrationResult":
        return cls(success=False, error=error, operation=operation)
