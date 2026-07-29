from __future__ import annotations

import uuid
from typing import Any

from workflow_engine.core.configuration import WorkflowConfig
from workflow_engine.core.kernel import WorkflowKernel
from workflow_engine.core.registry import WorkflowRegistry
from workflow_engine.executor.executor import ExecutionResult
from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.graph_builder import GraphBuilder
from workflow_engine.state.state_machine import WorkflowState
from workflow_engine.state.state_manager import StateManager


class WorkflowEngine:
    def __init__(self, kernel: WorkflowKernel, registry: WorkflowRegistry, state_manager: StateManager, config: WorkflowConfig | None = None):
        self._kernel = kernel
        self._registry = registry
        self._state_manager = state_manager
        self._config = config or WorkflowConfig()
        self._graphs: dict[str, WorkflowGraph] = {}

    async def create_workflow(self, config: dict[str, Any]) -> str:
        workflow_id = str(uuid.uuid4())
        graph = GraphBuilder.from_dict(config.get("graph", {}))
        self._graphs[workflow_id] = graph
        await self._state_manager.set_state(workflow_id, WorkflowState.CREATED)
        return workflow_id

    async def execute(self, workflow_id: str, context: dict[str, Any] | None = None) -> ExecutionResult:
        graph = self._graphs.get(workflow_id)
        if not graph:
            raise ValueError(f"Workflow {workflow_id} not found")
        await self._state_manager.set_state(workflow_id, WorkflowState.RUNNING)
        try:
            result = await self._kernel.run(graph, context or {}, workflow_id)
            await self._state_manager.set_state(workflow_id, WorkflowState.COMPLETED)
            return result
        except Exception:
            await self._state_manager.set_state(workflow_id, WorkflowState.FAILED)
            raise

    async def pause(self, workflow_id: str) -> None:
        current = await self._state_manager.get_state(workflow_id)
        if current not in (WorkflowState.RUNNING, WorkflowState.WAITING):
            raise ValueError(f"Cannot pause workflow {workflow_id} in state {current}")
        await self._state_manager.set_state(workflow_id, WorkflowState.PAUSED)

    async def resume(self, workflow_id: str) -> None:
        current = await self._state_manager.get_state(workflow_id)
        if current != WorkflowState.PAUSED:
            raise ValueError(f"Cannot resume workflow {workflow_id} in state {current}")
        await self._state_manager.set_state(workflow_id, WorkflowState.RUNNING)

    async def cancel(self, workflow_id: str) -> None:
        current = await self._state_manager.get_state(workflow_id)
        if current in (WorkflowState.COMPLETED, WorkflowState.CANCELLED):
            raise ValueError(f"Cannot cancel workflow {workflow_id} in state {current}")
        await self._state_manager.set_state(workflow_id, WorkflowState.CANCELLED)

    async def get_status(self, workflow_id: str) -> WorkflowState:
        return await self._state_manager.get_state(workflow_id)

    def get_graph(self, workflow_id: str) -> WorkflowGraph | None:
        return self._graphs.get(workflow_id)
