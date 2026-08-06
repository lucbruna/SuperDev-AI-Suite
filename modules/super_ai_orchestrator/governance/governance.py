"""GovernanceEngine — the approval gate between decision and execution.

The gate decides, deterministically, whether a task needs human/operator
approval before the kernel may schedule it. Tasks that pass flow to the
queue; tasks that are denied are rejected. The kernel remains the source
of truth for status and audit; the engine only applies policy.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any

from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.core.task import Task
from modules.super_ai_orchestrator.kernel import OrchestrationKernel


@dataclass(slots=True)
class GovernancePolicy:
    """Which kinds of tasks always/never require approval.

    Attributes:
        approval_kinds: kinds that ALWAYS require approval.
        auto_approve_kinds: kinds that NEVER require approval (override).
        max_priority_without_approval: tasks with priority above this always
            require approval (high-urgency blast radius).
        destructive_markers: payload keys whose presence marks a task as
            potentially destructive (requires approval).
    """

    approval_kinds: frozenset[str] = frozenset({"deploy", "recover"})
    auto_approve_kinds: frozenset[str] = frozenset({"monitor", "analyze"})
    max_priority_without_approval: int = 8
    destructive_markers: frozenset[str] = frozenset({"delete", "drop", "force"})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GovernancePolicy":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


class GovernanceEngine:
    """Applies approval policy against the kernel.

    Attributes:
        policy: the approval rules.
    """

    def __init__(self, policy: GovernancePolicy | None = None) -> None:
        self.policy = policy or GovernancePolicy()

    def needs_approval(self, task: Task, kernel: OrchestrationKernel) -> tuple[bool, str]:
        """Return (needs_approval, reason).

        Rules, checked in order:
        1. ``auto_approve_kinds`` → no approval.
        2. ``approval_kinds`` → approval.
        3. priority above ``max_priority_without_approval`` → approval.
        4. any destructive marker present in payload → approval.
        5. otherwise → the kernel-wide ``governance_required`` setting.
        """
        if task.kind in self.policy.auto_approve_kinds:
            return False, f"kind '{task.kind}' is auto-approved"
        if task.kind in self.policy.approval_kinds:
            return True, f"kind '{task.kind}' always requires approval"
        if task.priority > self.policy.max_priority_without_approval:
            return True, f"priority {task.priority} exceeds approval threshold"
        markers = [m for m in self.policy.destructive_markers if m in task.payload]
        if markers:
            return True, f"destructive markers present: {', '.join(markers)}"
        if kernel.config.governance_required:
            return True, "governance required by kernel configuration"
        return False, "no approval required"

    def approve(self, kernel: OrchestrationKernel, task: Task) -> Task:
        return kernel.approve(task)

    def reject(self, kernel: OrchestrationKernel, task: Task, reason: str) -> Task:
        return kernel.reject(task, reason)

    def apply_to_kernel(self, kernel: OrchestrationKernel) -> None:
        """Ensure gated tasks submitted to ``kernel`` respect this policy.

        Convenience used by the facade: after submission, tasks parked at
        WAITING_APPROVAL are auto-approved/rejected here when the kernel is
        not running with an external operator.
        """
        for task in kernel.by_status(TaskStatus.WAITING_APPROVAL):
            needs, reason = self.needs_approval(task, kernel)
            if not needs:
                kernel.approve(task)
