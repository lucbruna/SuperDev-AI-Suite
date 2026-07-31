"""Fluent builder for action definitions."""

from __future__ import annotations

from typing import Any, Callable

from automation.actions.action_models import ActionDefinition


class ActionBuilder:
    """Builds (ActionDefinition, handler) pairs with a fluent API."""

    def __init__(self) -> None:
        self._action_id = ""
        self._name = ""
        self._description = ""
        self._required: list[str] = []
        self._timeout: float | None = None
        self._retries = 0
        self._retry_delay = 0.1
        self._schema: dict[str, str] | None = None
        self._enabled = True
        self._handler: Callable[[dict[str, Any]], Any] | None = None

    def id(self, action_id: str) -> "ActionBuilder":
        self._action_id = action_id
        return self

    def name(self, name: str) -> "ActionBuilder":
        self._name = name
        return self

    def description(self, description: str) -> "ActionBuilder":
        self._description = description
        return self

    def required_params(self, *params: str) -> "ActionBuilder":
        self._required = list(params)
        return self

    def timeout(self, seconds: float) -> "ActionBuilder":
        self._timeout = seconds
        return self

    def retries(self, count: int, delay: float = 0.1) -> "ActionBuilder":
        self._retries = count
        self._retry_delay = delay
        return self

    def params_schema(self, schema: dict[str, str]) -> "ActionBuilder":
        self._schema = schema
        return self

    def enabled(self, enabled: bool) -> "ActionBuilder":
        self._enabled = enabled
        return self

    def handler(self, handler: Callable[[dict[str, Any]], Any]) -> "ActionBuilder":
        self._handler = handler
        return self

    def build(self) -> tuple[ActionDefinition, Callable[[dict[str, Any]], Any] | None]:
        definition = ActionDefinition(
            action_id=self._action_id,
            name=self._name,
            description=self._description,
            required_params=list(self._required),
            timeout=self._timeout,
            retries=self._retries,
            retry_delay=self._retry_delay,
            params_schema=dict(self._schema) if self._schema else None,
            enabled=self._enabled,
        )
        return definition, self._handler
