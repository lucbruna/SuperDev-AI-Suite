from __future__ import annotations

from collections.abc import Callable
from typing import Any


class RollbackEntry:
    def __init__(self, node_id: str, rollback_func: Callable[[], Any], workflow_id: str):
        self.node_id = node_id
        self.rollback_func = rollback_func
        self.workflow_id = workflow_id


class RollbackManager:
    def __init__(self):
        self._rollbacks: dict[str, list[RollbackEntry]] = {}

    def register_rollback(self, node_id: str, rollback_func: Callable[[], Any], workflow_id: str = "") -> None:
        key = workflow_id or node_id
        entry = RollbackEntry(node_id=node_id, rollback_func=rollback_func, workflow_id=key)
        self._rollbacks.setdefault(key, []).append(entry)

    async def execute_rollback(self, workflow_id: str) -> None:
        entries = self._rollbacks.pop(workflow_id, [])
        for entry in reversed(entries):
            try:
                result = entry.rollback_func()
                if hasattr(result, "__await__"):
                    await result
            except Exception:
                pass

    def get_history(self, workflow_id: str) -> list[dict[str, Any]]:
        entries = self._rollbacks.get(workflow_id, [])
        return [
            {"node_id": e.node_id, "workflow_id": e.workflow_id} for e in entries
        ]
