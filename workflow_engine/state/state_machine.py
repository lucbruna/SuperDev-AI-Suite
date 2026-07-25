from __future__ import annotations

from enum import StrEnum


class WorkflowState(StrEnum):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ROLLED_BACK = "ROLLED_BACK"


_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.CREATED: {WorkflowState.READY, WorkflowState.CANCELLED},
    WorkflowState.READY: {WorkflowState.RUNNING, WorkflowState.CANCELLED},
    WorkflowState.RUNNING: {
        WorkflowState.PAUSED, WorkflowState.WAITING, WorkflowState.BLOCKED,
        WorkflowState.RETRYING, WorkflowState.FAILED, WorkflowState.COMPLETED, WorkflowState.CANCELLED,
    },
    WorkflowState.PAUSED: {WorkflowState.RUNNING, WorkflowState.CANCELLED},
    WorkflowState.WAITING: {WorkflowState.RUNNING, WorkflowState.CANCELLED, WorkflowState.FAILED},
    WorkflowState.BLOCKED: {
        WorkflowState.WAITING, WorkflowState.RUNNING, WorkflowState.CANCELLED, WorkflowState.FAILED,
    },
    WorkflowState.RETRYING: {WorkflowState.RUNNING, WorkflowState.FAILED, WorkflowState.CANCELLED},
    WorkflowState.FAILED: {WorkflowState.RETRYING, WorkflowState.ROLLED_BACK, WorkflowState.READY},
    WorkflowState.COMPLETED: {WorkflowState.ROLLED_BACK},
    WorkflowState.CANCELLED: set(),
    WorkflowState.ROLLED_BACK: set(),
}


class TransitionRecord:
    def __init__(self, workflow_id: str, from_state: WorkflowState, to_state: WorkflowState):
        self.workflow_id = workflow_id
        self.from_state = from_state
        self.to_state = to_state

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
        }


class WorkflowStateMachine:
    def can_transition(self, from_state: WorkflowState, to_state: WorkflowState) -> bool:
        allowed = _TRANSITIONS.get(from_state, set())
        return to_state in allowed

    def transition(
        self, workflow_id: str, from_state: WorkflowState, to_state: WorkflowState,
    ) -> TransitionRecord:
        if not self.can_transition(from_state, to_state):
            raise ValueError(f"Invalid transition from {from_state.value} to {to_state.value}")
        return TransitionRecord(workflow_id=workflow_id, from_state=from_state, to_state=to_state)
