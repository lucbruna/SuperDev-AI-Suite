"""Approval gating for high-risk tasks (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_models import AgentTask, TaskStatus


class ApprovalManager:
    """Requires and resolves human approvals for gated tasks."""

    def __init__(self, events: OrchestratorEvents | None = None) -> None:
        self.events = events or OrchestratorEvents()
        self._pending: dict[str, dict[str, Any]] = {}

    def require(self, task: AgentTask, reason: str = "") -> None:
        task.approval_required = True
        task.status = TaskStatus.APPROVAL_REQUIRED
        self._pending[task.task_id] = {
            "task_id": task.task_id, "reason": reason,
            "approved": None, "approver": "",
        }
        self.events.publish(OrchestratorEventType.APPROVAL_REQUIRED,
                            {"task_id": task.task_id, "reason": reason})

    def resolve(self, task: AgentTask, approved: bool,
                approver: str = "") -> bool:
        pending = self._pending.pop(task.task_id, None)
        if pending is None:
            return False
        pending["approved"] = approved
        pending["approver"] = approver
        task.status = (TaskStatus.QUEUED if approved
                       else TaskStatus.CANCELLED)
        self.events.publish(OrchestratorEventType.APPROVAL_RESOLVED,
                            {"task_id": task.task_id,
                             "approved": approved, "approver": approver})
        return True

    def pending(self) -> list[dict[str, Any]]:
        return [dict(entry) for entry in self._pending.values()]

    def is_pending(self, task_id: str) -> bool:
        return task_id in self._pending
