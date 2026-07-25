from __future__ import annotations

from typing import Any

from workflow_engine.checkpoint.checkpoint import Checkpoint
from workflow_engine.core.registry import WorkflowRegistry
from workflow_engine.events.workflow_failed import WorkflowFailed
from workflow_engine.events.workflow_finished import WorkflowFinished
from workflow_engine.events.workflow_started import WorkflowStarted
from workflow_engine.executor.executor import ExecutionResult, WorkflowExecutor
from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.state.state_manager import StateManager


class EventDispatcher:
    def __init__(self):
        self._handlers: dict[str, list] = {}

    def register(self, event_type: str, handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def dispatch(self, event: Any) -> None:
        event_type = type(event).__name__
        for handler in self._handlers.get(event_type, []):
            await handler(event)


class WorkflowKernel:
    def __init__(self, executor: WorkflowExecutor, state_manager: StateManager, checkpoint: Checkpoint, registry: WorkflowRegistry):
        self._executor = executor
        self._state_manager = state_manager
        self._checkpoint = checkpoint
        self._registry = registry
        self._dispatcher = EventDispatcher()
        self._running: set[str] = set()

    async def run(self, graph: WorkflowGraph, context: dict[str, Any], workflow_id: str) -> ExecutionResult:
        self._running.add(workflow_id)
        started_event = WorkflowStarted(workflow_id=workflow_id, graph_id=graph.id, timestamp=__import__("datetime").datetime.now())
        await self._dispatcher.dispatch(started_event)
        try:
            if self._checkpoint:
                await self._checkpoint.save(workflow_id, graph, context)
            result = await self._executor.execute_graph(graph, context, workflow_id)
            finished_event = WorkflowFinished(workflow_id=workflow_id, status="completed", duration=result.duration, result=result)
            await self._dispatcher.dispatch(finished_event)
            return result
        except Exception as e:
            failed_event = WorkflowFailed(workflow_id=workflow_id, error=str(e), node_id="", retry_count=0)
            await self._dispatcher.dispatch(failed_event)
            raise
        finally:
            self._running.discard(workflow_id)

    def get_dispatcher(self) -> EventDispatcher:
        return self._dispatcher
