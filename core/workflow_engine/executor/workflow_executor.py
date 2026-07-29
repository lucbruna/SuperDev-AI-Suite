from __future__ import annotations

import asyncio
import time
from typing import Any

from workflow_engine.checkpoint.checkpoint import Checkpoint
from workflow_engine.core.registry import WorkflowRegistry
from workflow_engine.executor.executor import ExecutionResult
from workflow_engine.executor.task_executor import TaskExecutor
from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.graph_validator import GraphValidator
from workflow_engine.retry.retry_policy import RetryPolicy
from workflow_engine.retry.rollback_manager import RollbackManager


class WorkflowLifecycleExecutor:
    def __init__(
        self,
        registry: WorkflowRegistry,
        retry_policy: RetryPolicy | None = None,
        rollback_manager: RollbackManager | None = None,
        checkpoint: Checkpoint | None = None,
    ):
        self._registry = registry
        self._task_executor = TaskExecutor(registry)
        self._retry_policy = retry_policy or RetryPolicy()
        self._rollback_manager = rollback_manager or RollbackManager()
        self._checkpoint = checkpoint

    async def execute(
        self,
        graph: WorkflowGraph,
        context: dict[str, Any],
        workflow_id: str,
    ) -> ExecutionResult:
        validation = GraphValidator.validate(graph)
        if not validation.is_valid:
            return ExecutionResult(
                success=False,
                error=f"Graph validation failed: {[e.message for e in validation.errors]}",
                workflow_id=workflow_id,
            )

        execution_plan = self._build_execution_plan(graph)
        start = time.monotonic()

        if self._checkpoint:
            await self._checkpoint.save(workflow_id, graph, context)

        node_results = []
        for node in execution_plan:
            node_id = node.id
            attempt = 0
            while True:
                try:
                    nr = await self._task_executor.execute_node_direct(node, context)
                    node_results.append(nr)
                    if not nr.success:
                        if self._should_retry(attempt, nr.error):
                            attempt += 1
                            delay = self._retry_policy.get_delay(attempt)
                            await asyncio.sleep(delay)
                            continue
                        await self._rollback_manager.execute_rollback(workflow_id)
                        return ExecutionResult(
                            success=False,
                            error=nr.error,
                            node_results=node_results,
                            duration=time.monotonic() - start,
                            workflow_id=workflow_id,
                        )
                    self._rollback_manager.register_rollback(node_id, lambda: None)
                    if nr.output is not None:
                        context[node_id] = nr.output
                    break
                except Exception as e:
                    if self._should_retry(attempt, str(e)):
                        attempt += 1
                        delay = self._retry_policy.get_delay(attempt)
                        await asyncio.sleep(delay)
                        continue
                    await self._rollback_manager.execute_rollback(workflow_id)
                    return ExecutionResult(
                        success=False,
                        error=str(e),
                        node_results=node_results,
                        duration=time.monotonic() - start,
                        workflow_id=workflow_id,
                    )

        return ExecutionResult(
            success=True,
            output=context.copy(),
            node_results=node_results,
            duration=time.monotonic() - start,
            workflow_id=workflow_id,
        )

    def _build_execution_plan(self, graph: WorkflowGraph) -> list:
        return graph.topological_sort()

    def _should_retry(self, attempt: int, error: str | None) -> bool:
        return self._retry_policy.should_retry(attempt, error or "")
