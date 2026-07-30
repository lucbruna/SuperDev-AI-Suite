from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """Represents a single tool invocation."""
    tool_name: str
    params: dict[str, Any]
    result: dict[str, Any] | None = None
    status: str = "pending"
    started_at: float | None = None
    completed_at: float | None = None
    error: str | None = None
    execution_id: str = ""

    @property
    def duration(self) -> float:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return 0.0


@dataclass
class ToolRegistration:
    """Represents a registered tool in the registry."""
    name: str
    tool_class: type
    category: str
    version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)
    registered_at: float = field(default_factory=time.time)


@dataclass
class ToolContext:
    """Context passed to tools during execution."""
    execution_id: str
    user_id: str = ""
    session_id: str = ""
    environment: dict[str, Any] = field(default_factory=dict)
    permissions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
