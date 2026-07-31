"""Registry of action definitions and handlers."""

from __future__ import annotations

from typing import Any, Callable

from automation.actions.action_models import ActionDefinition


class ActionRegistry:
    """Stores action definitions alongside their handlers."""

    def __init__(self) -> None:
        self._definitions: dict[str, ActionDefinition] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}

    def register(self, definition: ActionDefinition,
                 handler: Callable[[dict[str, Any]], Any] | None) -> None:
        self._definitions[definition.action_id] = definition
        if handler is not None:
            self._handlers[definition.action_id] = handler

    def get_definition(self, action_id: str) -> ActionDefinition | None:
        return self._definitions.get(action_id)

    def get_handler(self, action_id: str) -> Callable[[dict[str, Any]], Any] | None:
        return self._handlers.get(action_id)

    def has(self, action_id: str) -> bool:
        return action_id in self._definitions

    def list(self) -> list[str]:
        return list(self._definitions)

    def remove(self, action_id: str) -> bool:
        removed = self._definitions.pop(action_id, None) is not None
        self._handlers.pop(action_id, None)
        return removed

    def snapshot(self) -> dict[str, int]:
        return {"actions": len(self._definitions)}
