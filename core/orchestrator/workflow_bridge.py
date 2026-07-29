"""Workflow Bridge — integration between Orchestrator and Workflow Engine.

Provides a clean API for the orchestrator to create, execute, pause,
resume, cancel, and monitor workflows managed by the core/workflow_engine/
module. Handles lifecycle mapping and event propagation.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

from .exceptions import OrchestratorError
from .types import ServiceStatus, SystemEvent, now_iso


class WorkflowBridge:
    """Bridge between the Orchestrator and the Workflow Engine.

    Wraps the core/workflow_engine/ module into the orchestrator's
    service architecture, providing lifecycle management and event
    propagation for all workflow operations.
    """

    # Map workflow engine states to orchestrator service states
    WORKFLOW_TO_SERVICE_STATUS = {
        "created": ServiceStatus.CREATED,
        "running": ServiceStatus.RUNNING,
        "paused": ServiceStatus.PAUSED,
        "completed": ServiceStatus.STOPPED,
        "failed": ServiceStatus.FAILED,
        "cancelled": ServiceStatus.STOPPED,
        "waiting": ServiceStatus.RUNNING,
    }

    def __init__(self, event_bus: Any = None) -> None:
        self._engine: Any = None
        self._event_bus = event_bus
        self._workflow_metadata: dict[str, dict[str, Any]] = {}
        self._running_workflows: dict[str, asyncio.Task[Any]] = {}

    async def initialize(self) -> bool:
        """Initialize the workflow engine bridge."""
        try:
            from core.workflow_engine.core.engine import WorkflowEngine
            from core.workflow_engine.core.kernel import WorkflowKernel
            from core.workflow_engine.core.registry import WorkflowRegistry
            from core.workflow_engine.state.state_manager import StateManager

            kernel = WorkflowKernel()
            registry = WorkflowRegistry()
            state_manager = StateManager()
            self._engine = WorkflowEngine(kernel, registry, state_manager)
            return True
        except ImportError as e:
            raise OrchestratorError(f"Failed to initialize WorkflowEngine: {e}")

    async def health(self) -> dict[str, Any]:
        """Check if the workflow engine is operational."""
        return {
            "initialized": self._engine is not None,
            "active_workflows": len(self._running_workflows),
            "total_workflows": len(self._workflow_metadata),
        }

    # ─── Workflow CRUD ────────────────────────────────────────────────────

    async def create_workflow(
        self,
        config: dict[str, Any],
        name: str = "",
        description: str = "",
    ) -> dict[str, Any]:
        """Create a new workflow definition."""
        if not self._engine:
            raise OrchestratorError("WorkflowEngine not initialized")

        workflow_id = await self._engine.create_workflow(config)

        self._workflow_metadata[workflow_id] = {
            "workflow_id": workflow_id,
            "name": name or f"Workflow-{workflow_id[:8]}",
            "description": description,
            "config": config,
            "status": "created",
            "created_at": now_iso(),
            "started_at": "",
            "completed_at": "",
            "execution_count": 0,
            "last_result": None,
        }

        if self._event_bus:
            await self._event_bus.publish(
                "workflow.created",
                {"workflow_id": workflow_id, "name": name},
                source="workflow_bridge",
            )

        return {
            "workflow_id": workflow_id,
            "name": self._workflow_metadata[workflow_id]["name"],
            "status": "created",
        }

    async def execute_workflow(
        self,
        workflow_id: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a workflow asynchronously."""
        if not self._engine:
            raise OrchestratorError("WorkflowEngine not initialized")
        if workflow_id not in self._workflow_metadata:
            raise OrchestratorError(f"Workflow {workflow_id} not found")

        meta = self._workflow_metadata[workflow_id]
        meta["status"] = "running"
        meta["started_at"] = now_iso()
        meta["execution_count"] += 1

        if self._event_bus:
            await self._event_bus.publish(
                "workflow.started",
                {"workflow_id": workflow_id},
                source="workflow_bridge",
            )

        task = asyncio.create_task(
            self._run_workflow(workflow_id, context or {}),
        )
        self._running_workflows[workflow_id] = task

        return {
            "workflow_id": workflow_id,
            "status": "running",
            "started_at": meta["started_at"],
        }

    async def _run_workflow(
        self, workflow_id: str, context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute workflow and capture results."""
        import time as tmod
        start = tmod.time()
        meta = self._workflow_metadata[workflow_id]

        try:
            result = await self._engine.execute(workflow_id, context)
            elapsed = round((tmod.time() - start) * 1000, 2)

            meta["status"] = "completed" if result.success else "failed"
            meta["completed_at"] = now_iso()
            meta["last_result"] = {
                "success": result.success,
                "output": getattr(result, "output", ""),
                "duration_ms": elapsed,
            }

            if self._event_bus:
                await self._event_bus.publish(
                    "workflow.completed" if result.success else "workflow.failed",
                    {"workflow_id": workflow_id, "duration_ms": elapsed},
                    source="workflow_bridge",
                )

            return meta["last_result"]

        except Exception as e:
            meta["status"] = "failed"
            meta["completed_at"] = now_iso()
            meta["last_result"] = {"success": False, "error": str(e)}

            if self._event_bus:
                await self._event_bus.publish(
                    "workflow.failed",
                    {"workflow_id": workflow_id, "error": str(e)},
                    source="workflow_bridge",
                )

            return {"success": False, "error": str(e)}

        finally:
            self._running_workflows.pop(workflow_id, None)

    async def pause_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Pause a running workflow."""
        if not self._engine:
            raise OrchestratorError("WorkflowEngine not initialized")
        try:
            await self._engine.pause(workflow_id)
            if workflow_id in self._workflow_metadata:
                self._workflow_metadata[workflow_id]["status"] = "paused"
            return {"workflow_id": workflow_id, "status": "paused"}
        except ValueError as e:
            raise OrchestratorError(str(e))

    async def resume_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Resume a paused workflow."""
        if not self._engine:
            raise OrchestratorError("WorkflowEngine not initialized")
        try:
            await self._engine.resume(workflow_id)
            if workflow_id in self._workflow_metadata:
                self._workflow_metadata[workflow_id]["status"] = "running"
            # Re-start async execution
            return await self.execute_workflow(workflow_id)
        except ValueError as e:
            raise OrchestratorError(str(e))

    async def cancel_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Cancel a workflow."""
        if not self._engine:
            raise OrchestratorError("WorkflowEngine not initialized")
        try:
            await self._engine.cancel(workflow_id)
            if workflow_id in self._workflow_metadata:
                self._workflow_metadata[workflow_id]["status"] = "cancelled"
                self._workflow_metadata[workflow_id]["completed_at"] = now_iso()
            # Cancel running task
            task = self._running_workflows.pop(workflow_id, None)
            if task:
                task.cancel()
            return {"workflow_id": workflow_id, "status": "cancelled"}
        except ValueError as e:
            raise OrchestratorError(str(e))

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """Get workflow status."""
        if not self._engine:
            raise OrchestratorError("WorkflowEngine not initialized")
        try:
            status = await self._engine.get_status(workflow_id)
        except Exception:
            status = None

        meta = self._workflow_metadata.get(workflow_id, {})
        return {
            "workflow_id": workflow_id,
            "engine_status": str(status) if status else "unknown",
            "metadata": meta,
            "is_running": workflow_id in self._running_workflows,
        }

    # ─── Query ────────────────────────────────────────────────────────────

    def list_workflows(
        self, status: str = "", limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List all workflows, optionally filtered by status."""
        workflows = list(self._workflow_metadata.values())
        if status:
            workflows = [w for w in workflows if w["status"] == status]
        workflows.sort(key=lambda w: w["created_at"], reverse=True)
        return workflows[:limit]

    def get_statistics(self) -> dict[str, Any]:
        """Get workflow engine statistics."""
        workflows = self._workflow_metadata.values()
        total = len(workflows)
        by_status: dict[str, int] = {}
        total_executions = 0

        for w in workflows:
            by_status[w["status"]] = by_status.get(w["status"], 0) + 1
            total_executions += w.get("execution_count", 0)

        return {
            "total_workflows": total,
            "active_workflows": len(self._running_workflows),
            "by_status": by_status,
            "total_executions": total_executions,
            "engine_initialized": self._engine is not None,
        }
