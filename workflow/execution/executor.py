from __future__ import annotations

import logging
from typing import Any, Callable


class StepExecutor:
    """Executes individual steps within a workflow."""

    def __init__(self) -> None:
        self._actions: dict[str, Callable[..., Any]] = {}
        self._log = logging.getLogger("superdev.workflow.execution.executor")

    def register(self, name: str, action: Callable[..., Any]) -> None:
        self._actions[name] = action

    def execute(self, action: str, params: dict[str, Any] | None = None) -> Any:
        fn = self._actions.get(action)
        if not fn:
            raise ValueError(f"Unknown action: {action}")
        return fn(**(params or {}))

    def can_execute(self, action: str) -> bool:
        return action in self._actions
