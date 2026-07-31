"""Configuration for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass
class CollaborationConfig:
    """Runtime configuration for the engine.

    Attributes mirror the knobs used across the subsystems; every field
    has a sensible default so ``build_engine()`` works out of the box.
    """

    engine_name: str = "collaboration"
    enabled: bool = True
    workspace_name: str = "SuperDev"
    default_timezone: str = "UTC"
    locale: str = "pt_BR"
    max_task_children: int = 50
    default_approval_flow: str = "manager"
    mention_prefix: str = "@"
    agent_prefix: str = "agent:"
    review_max_findings: int = 100
    chat_history_limit: int = 200
    retention_days: int = 365
    log_level: str = "INFO"
    extra: dict[str, Any] = field(default_factory=dict)

    def merge(self, **overrides: Any) -> "CollaborationConfig":
        """Returns a copy with the given fields replaced."""
        return replace(self, **overrides)
