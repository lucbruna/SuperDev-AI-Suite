"""Knowledge kernel — low-level execution core.

Runs pipeline stages with state tracking, error capture and cancellation
checks. The kernel is the single place that touches the state machine during
execution, so managers and agents stay thin.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_state import KnowledgeState
from modules.ai_code_knowledge_graph.core.exceptions import KnowledgeError

logger = logging.getLogger(__name__)

StageFn = Callable[[KnowledgeContext], Any]


class KnowledgeKernel:
    """Executes named operations against a knowledge context."""

    def execute(self, ctx: KnowledgeContext, name: str, state: KnowledgeState, fn: StageFn) -> dict[str, Any]:
        """Run ``fn`` under the given state; returns a structured result."""
        ctx.state.set_state(state, context=f"kernel:{name}")
        ctx.publish(f"kernel.{name}.started", {})
        started = time.time()
        try:
            payload = fn(ctx)
        except KnowledgeError as exc:
            ctx.state.mark_error(f"Operation '{name}' failed: {exc.message}", exc.context)
            ctx.publish(f"kernel.{name}.failed", {"error": exc.message})
            raise
        except Exception as exc:  # noqa: BLE001 — normalize unexpected failures
            ctx.state.mark_error(f"Operation '{name}' failed: {exc}", {"exception": type(exc).__name__})
            ctx.publish(f"kernel.{name}.failed", {"error": str(exc)})
            raise KnowledgeError(f"Operation '{name}' failed: {exc}", cause=exc) from exc
        result = {"operation": name, "payload": payload, "elapsed_seconds": round(time.time() - started, 3)}
        ctx.publish(f"kernel.{name}.completed", result)
        return result

    def execute_many(
        self,
        ctx: KnowledgeContext,
        operations: list[tuple[str, KnowledgeState, StageFn]],
    ) -> list[dict[str, Any]]:
        """Run several operations in order, honouring cancellation."""
        results: list[dict[str, Any]] = []
        for name, state, fn in operations:
            if ctx.cancelled:
                break
            results.append(self.execute(ctx, name, state, fn))
        return results
