"""Data models for triggers."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class TriggerDefinition:
    """A registered trigger with a declarative or callable condition."""

    trigger_id: str
    name: str
    trigger_type: str = "condition"  # event | condition | time
    condition: dict[str, Any] | None = None  # declarative: {"field","op","value"}
    predicate: Callable[[dict[str, Any]], bool] | None = None
    config: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "name": self.name,
            "trigger_type": self.trigger_type,
            "condition": self.condition,
            "config": dict(self.config),
            "enabled": self.enabled,
        }


@dataclass
class TriggerEvent:
    """An event delivered to the trigger router."""

    event_type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {"event_type": self.event_type,
                "data": dict(self.data), "timestamp": self.timestamp}
