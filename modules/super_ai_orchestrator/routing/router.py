"""Router — maps a task kind to the agent that will own it.

The router is a pure function of the RoutingConfig capability map:
- if the kind is mapped, the first capable agent wins, unless an
  ``owner_hint`` is given that is also capable (hints are honored only
  when the hinted agent can actually handle the kind);
- unknown kinds fall back to ``fallback_owner`` unless
  ``require_capability`` is set, in which case routing raises.
"""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.config import RoutingConfig


class Router:
    """Deterministic kind -> owner routing.

    Attributes:
        config: capability map and fallback behaviour.
    """

    def __init__(self, config: RoutingConfig | None = None) -> None:
        self.config = config or RoutingConfig()

    def route(self, kind: str, owner_hint: str | None = None) -> tuple[str, list[str]]:
        """Return (owner, candidates) for the given kind.

        Raises:
            ValueError: if the kind is unknown and require_capability is on.
        """
        candidates = list(self.config.capability_map.get(kind, ()))
        if not candidates:
            if self.config.require_capability:
                raise ValueError(f"no agent capable of kind '{kind}'")
            return self.config.fallback_owner, []
        if owner_hint and owner_hint in candidates:
            return owner_hint, candidates
        return candidates[0], candidates

    def owners(self) -> tuple[str, ...]:
        """All agent names referenced by the capability map."""
        seen: list[str] = []
        for agents in self.config.capability_map.values():
            for name in agents:
                if name not in seen:
                    seen.append(name)
        return tuple(seen)

    def to_dict(self) -> dict[str, Any]:
        return self.config.to_dict()
