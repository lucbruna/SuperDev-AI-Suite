"""Container lifecycle."""
from __future__ import annotations
from typing import Any, Dict, List

class ContainerLifecycle:
    def __init__(self) -> None:
        self._states: Dict[str, List[str]] = {}
    def track(self, container_id: str, initial_state: str = "created") -> Dict[str, Any]:
        self._states[container_id] = [initial_state]
        return {"container_id": container_id, "state": initial_state}
    def transition(self, container_id: str, new_state: str) -> bool:
        if container_id not in self._states:
            return False
        self._states[container_id].append(new_state)
        return True
    def get_history(self, container_id: str) -> List[str]:
        return self._states.get(container_id, [])
    def current_state(self, container_id: str) -> str:
        history = self._states.get(container_id, [])
        return history[-1] if history else "unknown"
    def list_containers(self) -> List[str]:
        return list(self._states.keys())
    def count(self) -> int:
        return len(self._states)
