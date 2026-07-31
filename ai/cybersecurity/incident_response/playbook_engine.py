"""
Incident Response Playbook Engine
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class PlaybookStep:
    step_id: str
    name: str
    description: str = ""
    status: StepStatus = StepStatus.PENDING
    assignee: str = ""
    notes: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class Playbook:
    playbook_id: str
    name: str
    description: str = ""
    steps: list[PlaybookStep] = field(default_factory=list)
    triggered: bool = False
    incident_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class PlaybookEngine:
    def __init__(self):
        self.playbooks: dict[str, Playbook] = {}
        self.templates: dict[str, list[dict[str, str]]] = {}

    def register_template(self, name: str, steps: list[dict[str, str]]) -> None:
        self.templates[name] = steps

    def create_playbook(self, name: str, incident_id: str, template_name: str = None) -> Playbook:
        playbook_id = hashlib.sha256(f"{name}{incident_id}".encode()).hexdigest()[:16]
        steps = []
        if template_name and template_name in self.templates:
            for i, step_data in enumerate(self.templates[template_name]):
                steps.append(PlaybookStep(step_id=f"step_{i}", name=step_data.get("name", f"Step {i+1}"), description=step_data.get("description", "")))
        playbook = Playbook(playbook_id=playbook_id, name=name, incident_id=incident_id, steps=steps)
        self.playbooks[playbook_id] = playbook
        return playbook

    def start_step(self, playbook_id: str, step_id: str) -> bool:
        playbook = self.playbooks.get(playbook_id)
        if playbook:
            for step in playbook.steps:
                if step.step_id == step_id:
                    step.status = StepStatus.IN_PROGRESS
                    step.started_at = datetime.now()
                    return True
        return False

    def complete_step(self, playbook_id: str, step_id: str, notes: str = "") -> bool:
        playbook = self.playbooks.get(playbook_id)
        if playbook:
            for step in playbook.steps:
                if step.step_id == step_id:
                    step.status = StepStatus.COMPLETED
                    step.completed_at = datetime.now()
                    step.notes = notes
                    return True
        return False

    def get_progress(self, playbook_id: str) -> dict[str, Any]:
        playbook = self.playbooks.get(playbook_id)
        if not playbook:
            return {"total": 0, "completed": 0, "percentage": 0}
        total = len(playbook.steps)
        completed = sum(1 for s in playbook.steps if s.status == StepStatus.COMPLETED)
        return {"total": total, "completed": completed, "percentage": (completed / max(total, 1)) * 100}

    def get_playbook(self, playbook_id: str) -> Playbook | None:
        return self.playbooks.get(playbook_id)

    def get_pending_steps(self, playbook_id: str) -> list[PlaybookStep]:
        playbook = self.playbooks.get(playbook_id)
        if playbook:
            return [s for s in playbook.steps if s.status == StepStatus.PENDING]
        return []

    def count(self) -> int:
        return len(self.playbooks)
