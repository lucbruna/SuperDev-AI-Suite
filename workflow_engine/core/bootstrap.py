from __future__ import annotations

from workflow_engine.checkpoint.checkpoint import Checkpoint
from workflow_engine.core.configuration import WorkflowConfig
from workflow_engine.core.engine import WorkflowEngine
from workflow_engine.core.kernel import WorkflowKernel
from workflow_engine.core.registry import WorkflowRegistry
from workflow_engine.executor.executor import WorkflowExecutor
from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.scheduler.scheduler import WorkflowScheduler
from workflow_engine.state.state_manager import StateManager


class Bootstrap:
    @staticmethod
    def initialize(config: WorkflowConfig | None = None) -> WorkflowEngine:
        registry = WorkflowRegistry()
        state_manager = StateManager()
        WorkflowGraph()
        executor = WorkflowExecutor(registry)
        checkpoint = Checkpoint()
        WorkflowScheduler()
        kernel = WorkflowKernel(executor, state_manager, checkpoint, registry)
        engine = WorkflowEngine(kernel, registry, state_manager, config)
        return engine
