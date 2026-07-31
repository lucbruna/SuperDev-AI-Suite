"""Prefix-based action routing with fallback."""

from __future__ import annotations

from typing import Any, Callable

from automation.actions.action_registry import ActionRegistry


class ActionRouter:
    """Routes actions to handlers by prefix or registry lookup."""

    def __init__(self, registry: ActionRegistry | None = None) -> None:
        self.registry = registry or ActionRegistry()
        self._prefixes: dict[str, Callable[[str, dict[str, Any]], Any]] = {}

    def register_prefix(self, prefix: str,
                        handler: Callable[[str, dict[str, Any]], Any]) -> None:
        self._prefixes[prefix] = handler

    def can_route(self, action_id: str) -> bool:
        if self.registry.has(action_id):
            return True
        return any(action_id.startswith(p) for p in self._prefixes)

    def route(self, action_id: str, params: dict[str, Any]) -> Any:
        if self.registry.has(action_id):
            handler = self.registry.get_handler(action_id)
            if handler is not None:
                return handler(params)
        for prefix in sorted(self._prefixes, key=len, reverse=True):
            if action_id.startswith(prefix):
                return self._prefixes[prefix](action_id, params)
        raise KeyError(f"no route for action: {action_id}")
