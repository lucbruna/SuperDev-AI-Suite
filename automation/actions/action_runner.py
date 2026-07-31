"""Runs actions with retries and timeout measurement."""

from __future__ import annotations

import time
from typing import Any

from automation.actions.action_models import ActionDefinition, ActionResult
from automation.actions.action_registry import ActionRegistry
from automation.automation_interfaces import ActionExecutor


class ActionRunner(ActionExecutor):
    """Implements the core ActionExecutor interface with retries."""

    def __init__(self, registry: ActionRegistry | None = None) -> None:
        self.registry = registry or ActionRegistry()

    # -- core interface ----------------------------------------------------
    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Single-shot execution (raises on error)."""
        handler = self.registry.get_handler(action)
        if handler is None:
            raise KeyError(f"no handler for action: {action}")
        result = handler(dict(params))
        return result if isinstance(result, dict) else {"result": result}

    # -- envelope execution ------------------------------------------------
    def run(self, definition: ActionDefinition,
            params: dict[str, Any]) -> ActionResult:
        handler = self.registry.get_handler(definition.action_id)
        if handler is None:
            return ActionResult(definition.action_id, False,
                                error="no handler registered")
        attempts = 0
        while True:
            attempts += 1
            start = time.monotonic()
            try:
                result = handler(dict(params))
                elapsed = (time.monotonic() - start) * 1000
                if definition.timeout is not None and elapsed / 1000 > definition.timeout:
                    raise TimeoutError(
                        f"action '{definition.action_id}' exceeded timeout "
                        f"of {definition.timeout}s")
                return ActionResult(definition.action_id, True, result=result,
                                    attempts=attempts,
                                    duration_ms=round(elapsed, 3))
            except Exception as exc:  # noqa: BLE001
                if attempts <= definition.retries:
                    time.sleep(definition.retry_delay)
                    continue
                return ActionResult(
                    definition.action_id, False, error=str(exc),
                    attempts=attempts,
                    duration_ms=round((time.monotonic() - start) * 1000, 3))
