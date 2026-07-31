"""Workflow engine."""
import uuid

from .models import (
    ApprovalRecord,
    StepStatus,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStatus,
    WorkflowStep,
)


class WorkflowEngine:
    def __init__(self):
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._steps: dict[str, WorkflowStep] = {}
        self._instances: dict[str, WorkflowInstance] = {}
        self._approvals: list[ApprovalRecord] = []

    def create_definition(self, defn: WorkflowDefinition) -> WorkflowDefinition:
        self._definitions[defn.workflow_id] = defn
        return defn

    def get_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        return self._definitions.get(workflow_id)

    def activate_definition(self, workflow_id: str) -> bool:
        defn = self._definitions.get(workflow_id)
        if not defn:
            return False
        defn.status = WorkflowStatus.ACTIVE
        return True

    def add_step(self, step: WorkflowStep) -> WorkflowStep:
        self._steps[step.step_id] = step
        return step

    def get_workflow_steps(self, workflow_id: str) -> list[WorkflowStep]:
        steps = [s for s in self._steps.values() if s.workflow_id == workflow_id]
        return sorted(steps, key=lambda s: s.order)

    def start_instance(self, instance: WorkflowInstance) -> WorkflowInstance:
        self._instances[instance.instance_id] = instance
        return instance

    def get_instance(self, instance_id: str) -> WorkflowInstance | None:
        return self._instances.get(instance_id)

    def complete_step(self, step_id: str, result: str = "completed") -> bool:
        step = self._steps.get(step_id)
        if not step:
            return False
        step.status = StepStatus.COMPLETED
        step.result = result
        return True

    def approve_step(self, step_id: str, approver: str, decision: str, comments: str = "") -> ApprovalRecord:
        step = self._steps.get(step_id)
        record = ApprovalRecord(
            record_id=str(uuid.uuid4())[:8],
            step_id=step_id,
            approver=approver,
            decision=decision,
            comments=comments,
        )
        if step:
            step.status = StepStatus.COMPLETED
            step.result = decision
        self._approvals.append(record)
        return record

    def get_approvals(self, instance_id: str | None = None) -> list[ApprovalRecord]:
        if instance_id:
            return [a for a in self._approvals if a.instance_id == instance_id]
        return list(self._approvals)

    def get_stats(self) -> dict:
        instances = list(self._instances.values())
        return {
            "definitions": len(self._definitions),
            "steps": len(self._steps),
            "instances": len(instances),
            "active": len([i for i in instances if i.status == WorkflowStatus.ACTIVE]),
            "approvals": len(self._approvals),
        }
