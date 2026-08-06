"""Routing configuration: how task kinds map to capable agents."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any

from modules.super_ai_orchestrator.config.base import apply_overrides

DEFAULT_CAPABILITY_MAP: dict[str, list[str]] = {
    "analyze": ["architect", "reviewer", "security", "infrastructure"],
    "plan": ["planner", "architect"],
    "develop": ["developer"],
    "repair": ["developer", "infrastructure", "recovery"],
    "evolve": ["evolution", "architect"],
    "workflow": ["workflow"],
    "document": ["documentation"],
    "monitor": ["monitoring"],
    "recover": ["recovery"],
    "deploy": ["infrastructure"],
    "review": ["reviewer", "security"],
    "coordinate": ["coordinator"],
    "agent": ["coordinator"],
}


@dataclass(slots=True)
class RoutingConfig:
    """Maps task kinds to the agent names capable of executing them.

    Attributes:
        fallback_owner: agent used when no rule matches the task kind.
        require_capability: reject tasks whose kind no agent can handle.
        capability_map: kind → list of capable agent names.
    """

    fallback_owner: str = "coordinator"
    require_capability: bool = True
    capability_map: dict[str, list[str]] = field(
        default_factory=lambda: dict(DEFAULT_CAPABILITY_MAP)
    )

    def resolve(self, overrides: dict[str, Any] | None = None) -> "RoutingConfig":
        return apply_overrides(self, overrides)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RoutingConfig":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})
