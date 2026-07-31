"""Data models for actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionDefinition:
    """A registered action with execution metadata."""

    action_id: str
    name: str
    description: str = ""
    required_params: list[str] = field(default_factory=list)
    timeout: float | None = None  # seconds (soft, measured)
    retries: int = 0
    retry_delay: float = 0.1
    params_schema: dict[str, str] | None = None  # field -> type name
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "name": self.name,
            "description": self.description,
            "required_params": list(self.required_params),
            "timeout": self.timeout,
            "retries": self.retries,
            "enabled": self.enabled,
        }


@dataclass
class ActionResult:
    """Envelope returned by action execution."""

    action_id: str
    success: bool
    result: Any = None
    error: str | None = None
    attempts: int = 1
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "attempts": self.attempts,
            "duration_ms": self.duration_ms,
        }
