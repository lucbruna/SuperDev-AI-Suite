"""Response playbooks."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class PlaybookStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class PlaybookStep:
    def __init__(self, step_id: str, name: str, action: str, details: str = "") -> None:
        self.step_id = step_id
        self.name = name
        self.action = action
        self.details = details
        self.order = 0


class ResponsePlaybook:
    def __init__(self, name: str, description: str = "") -> None:
        self.playbook_id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.status = PlaybookStatus.DRAFT
        self.steps: list[PlaybookStep] = []
        self.created_at = time.time()


class PlaybookManager:
    def __init__(self) -> None:
        self._playbooks: dict[str, ResponsePlaybook] = {}
        self._executions: list[dict[str, Any]] = []

    def create_playbook(self, name: str, description: str = "") -> ResponsePlaybook:
        pb = ResponsePlaybook(name, description)
        self._playbooks[pb.playbook_id] = pb
        return pb

    def add_step(self, playbook_id: str, name: str, action: str, details: str = "") -> bool:
        pb = self._playbooks.get(playbook_id)
        if pb:
            step = PlaybookStep(str(uuid.uuid4())[:8], name, action, details)
            step.order = len(pb.steps) + 1
            pb.steps.append(step)
            return True
        return False

    def activate(self, playbook_id: str) -> bool:
        pb = self._playbooks.get(playbook_id)
        if pb:
            pb.status = PlaybookStatus.ACTIVE
            return True
        return False

    def execute(self, playbook_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        pb = self._playbooks.get(playbook_id)
        if not pb or pb.status != PlaybookStatus.ACTIVE:
            return {"error": "playbook_not_active"}
        execution = {
            "execution_id": str(uuid.uuid4())[:8],
            "playbook_id": playbook_id,
            "steps_completed": 0,
            "total_steps": len(pb.steps),
            "timestamp": time.time(),
            "status": "completed",
        }
        execution["steps_completed"] = len(pb.steps)
        self._executions.append(execution)
        return execution

    def get_playbook(self, playbook_id: str) -> dict[str, Any] | None:
        pb = self._playbooks.get(playbook_id)
        if pb:
            return {
                "id": pb.playbook_id,
                "name": pb.name,
                "status": pb.status.value,
                "steps": len(pb.steps),
                "created_at": pb.created_at,
            }
        return None

    def list_playbooks(self, status: PlaybookStatus | None = None) -> list[str]:
        if status:
            return [p.playbook_id for p in self._playbooks.values() if p.status == status]
        return list(self._playbooks.keys())

    def get_executions(self, playbook_id: str = "", limit: int = 50) -> list[dict[str, Any]]:
        execs = self._executions
        if playbook_id:
            execs = [e for e in execs if e["playbook_id"] == playbook_id]
        return execs[-limit:]
