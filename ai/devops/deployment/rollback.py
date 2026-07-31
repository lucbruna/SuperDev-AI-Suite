"""Rollback manager."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class RollbackManager:
    def __init__(self) -> None:
        self._history: List[Dict[str, Any]] = []
    def record(self, deployment: str, from_version: str, to_version: str, reason: str = "") -> Dict[str, Any]:
        entry = {"deployment": deployment, "from_version": from_version, "to_version": to_version, "reason": reason, "timestamp": time.time()}
        self._history.append(entry)
        return entry
    def rollback(self, deployment: str, target_version: str) -> Dict[str, Any]:
        return {"deployment": deployment, "target_version": target_version, "status": "rolled_back"}
    def get_history(self, deployment: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        history = self._history
        if deployment:
            history = [h for h in history if h["deployment"] == deployment]
        return history[-limit:]
    def count(self) -> int:
        return len(self._history)
