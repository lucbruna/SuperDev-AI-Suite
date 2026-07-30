from __future__ import annotations

from typing import Any, Callable

from .reasoning_context import ReasoningContext
from .reasoning_models import ReasoningResult


class ReasoningRouter:
    """Routes reasoning requests to appropriate handlers based on context."""

    def __init__(self):
        self._routes: list[tuple[Callable[[ReasoningContext], bool], Callable[[ReasoningContext], Any]]] = []

    def add_route(self, matcher: Callable[[ReasoningContext], bool], handler: Callable[[ReasoningContext], Any]) -> None:
        self._routes.append((matcher, handler))

    async def route(self, context: ReasoningContext) -> Any:
        for matcher, handler in self._routes:
            if matcher(context):
                result = handler(context)
                if hasattr(result, "__await__"):
                    return await result
                return result
        raise ValueError(f"No route matches context {context.context_id}")

    def clear(self) -> None:
        self._routes.clear()
