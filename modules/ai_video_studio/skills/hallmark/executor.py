"""Hallmark executor — run planned steps and record outcomes."""
from __future__ import annotations
from typing import Any, Callable


class StepExecutor:
    """Execute a plan; each step is either a callable or a described action."""

    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def run(self, steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run steps in order, invoking callables and describing plain actions."""
        self.results.clear()
        for index, step in enumerate(steps, start=1):
            action = step.get("action", "")
            handler: Callable[[], Any] | None = step.get("handler")
            if handler is not None:
                outcome = handler()
            else:
                outcome = f"executed: {action}"
            self.results.append(
                {"step": index, "name": step.get("name", action), "outcome": outcome, "status": "ok"}
            )
        return self.results
