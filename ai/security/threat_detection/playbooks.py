"""Response playbooks."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time, uuid

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
        self.steps: List[PlaybookStep] = []
        self.created_at = time.time()

class PlaybookManager:
    def __init__(self) -> None:
        self._playbooks: Dict[str, ResponsePlaybook] = {}
        self._executions: List[Dict[str, Any]] = []
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
    def execute(self, playbook_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pb = self._playbooks.get(playbook_id)
        if not pb or pb.status != PlaybookStatus.ACTIVE:
            return {"error": "playbook_not_active"}
        execution = {"execution_id": str(uuid.uuid4())[:8], "playbook_id": playbook_id, "steps_completed": 0, "total_steps": len(pb.steps), "timestamp": time.time(), "status": "completed"}
        execution["steps_completed"] = len(pb.steps)
        self._executions.append(execution)
        return execution
    def get_playbook(self, playbook_id: str) -> Optional[Dict[str, Any]]:
        pb = self._playbooks.get(playbook_id)
        if pb:
            return {"id": pb.playbook_id, "name": pb.name, "status": pb.status.value, "steps": len(pb.steps), "created_at": pb.created_at}
        return None
    def list_playbooks(self, status: Optional[PlaybookStatus] = None) -> List[str]:
        if status:
            return [p.playbook_id for p in self._playbooks.values() if p.status == status]
        return list(self._playbooks.keys())
    def get_executions(self, playbook_id: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        execs = self._executions
        if playbook_id:
            execs = [e for e in execs if e["playbook_id"] == playbook_id]
        return execs[-limit:]
