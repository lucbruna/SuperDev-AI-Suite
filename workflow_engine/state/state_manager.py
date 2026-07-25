from __future__ import annotations

from typing import Optional

from workflow_engine.state.state_machine import WorkflowState, WorkflowStateMachine, TransitionRecord


class StateManager:
    def __init__(self):
        self._states: dict[str, WorkflowState] = {}
        self._history: dict[str, list[TransitionRecord]] = {}
        self._machine = WorkflowStateMachine()

    async def get_state(self, workflow_id: str) -> Optional[WorkflowState]:
        return self._states.get(workflow_id)

    async def set_state(self, workflow_id: str, new_state: WorkflowState) -> TransitionRecord:
        current = self._states.get(workflow_id, WorkflowState.CREATED)
        record = self._machine.transition(workflow_id, current, new_state)
        self._states[workflow_id] = new_state
        self._history.setdefault(workflow_id, []).append(record)
        return record

    async def get_history(self, workflow_id: str) -> list[TransitionRecord]:
        return self._history.get(workflow_id, [])

    def get_state_sync(self, workflow_id: str) -> Optional[WorkflowState]:
        return self._states.get(workflow_id)

    def set_state_sync(self, workflow_id: str, new_state: WorkflowState) -> TransitionRecord:
        current = self._states.get(workflow_id, WorkflowState.CREATED)
        record = self._machine.transition(workflow_id, current, new_state)
        self._states[workflow_id] = new_state
        self._history.setdefault(workflow_id, []).append(record)
        return record
