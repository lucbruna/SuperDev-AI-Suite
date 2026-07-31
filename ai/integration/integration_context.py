"""
Integration Context - Request/response context management
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ContextVariable:
    key: str
    value: Any
    scope: str = "request"
    source: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class IntegrationContext:
    def __init__(self):
        self.variables: dict[str, ContextVariable] = {}
        self.headers: dict[str, str] = {}
        self.metadata: dict[str, Any] = {}
        self.trace_id: str = ""
        self.span_id: str = ""
        self.parent_span_id: str = ""
        self.start_time: datetime = field(default_factory=datetime.now)

    def set_variable(self, key: str, value: Any, scope: str = "request", source: str = "") -> ContextVariable:
        var = ContextVariable(key=key, value=value, scope=scope, source=source)
        self.variables[key] = var
        return var

    def get_variable(self, key: str) -> Any | None:
        var = self.variables.get(key)
        return var.value if var else None

    def get_variables(self, scope: str = None) -> dict[str, Any]:
        if scope:
            return {k: v.value for k, v in self.variables.items() if v.scope == scope}
        return {k: v.value for k, v in self.variables.items()}

    def remove_variable(self, key: str) -> bool:
        if key in self.variables:
            del self.variables[key]
            return True
        return False

    def set_header(self, key: str, value: str) -> None:
        self.headers[key] = value

    def get_header(self, key: str) -> str | None:
        return self.headers.get(key)

    def set_trace(self, trace_id: str, span_id: str = "", parent_span_id: str = "") -> None:
        self.trace_id = trace_id
        self.span_id = span_id or hashlib.sha256(trace_id.encode()).hexdigest()[:16]
        self.parent_span_id = parent_span_id

    def create_child_context(self) -> "IntegrationContext":
        child = IntegrationContext()
        child.headers = self.headers.copy()
        child.metadata = self.metadata.copy()
        child.trace_id = self.trace_id
        child.parent_span_id = self.span_id
        child.span_id = hashlib.sha256(f"{self.span_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        return child

    def to_dict(self) -> dict[str, Any]:
        return {
            "variables": self.get_variables(),
            "headers": self.headers,
            "metadata": self.metadata,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "elapsed_ms": (datetime.now() - self.start_time).total_seconds() * 1000,
        }

    def clear(self) -> None:
        self.variables.clear()
        self.headers.clear()
        self.metadata.clear()

    def count(self) -> int:
        return len(self.variables)
