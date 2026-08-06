"""TaskExecutor — dispatches a task to its kind handler.

Handlers are registered per task kind. Out of the box every known kind has a
deterministic default handler that records a delegated stub result, so the
full pipeline runs end-to-end. Real integrations override these handlers
later (they receive the OrchestrationContext and return a result dict).
"""
from __future__ import annotations

from typing import Any, Callable

from modules.super_ai_orchestrator.core.context import OrchestrationContext

Handler = Callable[[OrchestrationContext], dict[str, Any]]

_KNOWN_KINDS: tuple[str, ...] = (
    "analyze",
    "plan",
    "develop",
    "repair",
    "evolve",
    "review",
    "monitor",
    "recover",
    "document",
    "deploy",
    "workflow",
    "coordinate",
    "agent",
)


def default_handlers() -> dict[str, Handler]:
    """Deterministic stub handlers for every known kind.

    Each handler returns a marked stub result so the pipeline works without
    any integration installed. The ``delegated_to`` field mirrors the
    decision (owner) when present.
    """

    def make_stub(kind: str) -> Handler:
        def stub(context: OrchestrationContext) -> dict[str, Any]:
            task = context.task
            return {
                "status": "delegated",
                "kind": kind,
                "title": task.title,
                "handler": "default",
                "owner": task.owner,
                "llm": task.llm,
                "plan": [step["action"] for step in context.plan],
            }

        return stub

    return {kind: make_stub(kind) for kind in _KNOWN_KINDS}


class TaskExecutor:
    """Registry + dispatcher of kind handlers.

    Attributes:
        handlers: kind -> handler callable.
    """

    def __init__(self) -> None:
        self.handlers: dict[str, Handler] = default_handlers()

    def register(self, kind: str, handler: Handler) -> None:
        """Register (or replace) the handler for ``kind``."""
        if not callable(handler):
            raise TypeError("handler must be callable")
        self.handlers[kind] = handler

    def install_real_handlers(self) -> int:
        """Register the real sibling-integration handlers on top of defaults.

        Replaces the deterministic stub handlers for the task kinds that map
        to a wired sibling connector (repair, recover, monitor, analyze,
        develop). Returns the number of handlers installed. Handlers degrade
        to a stub-like ``delegated`` result when a sibling is unavailable.
        """
        from modules.super_ai_orchestrator.execution.real_handlers import real_handlers

        installed = 0
        for kind, handler in real_handlers().items():
            self.register(kind, handler)
            installed += 1
        return installed

    def unregister(self, kind: str) -> bool:
        return self.handlers.pop(kind, None) is not None

    def supports(self, kind: str) -> bool:
        return kind in self.handlers

    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted(self.handlers.keys()))

    def execute(self, context: OrchestrationContext) -> dict[str, Any]:
        """Run the handler for ``context.task.kind``.

        Raises:
            KeyError: if no handler is registered for the task kind.
        """
        handler = self.handlers.get(context.task.kind)
        if handler is None:
            raise KeyError(f"no handler registered for kind '{context.task.kind}'")
        return handler(context)
