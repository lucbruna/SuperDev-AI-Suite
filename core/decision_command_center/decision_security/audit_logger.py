from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._logs: List[Dict[str, Any]] = []
        self._max_logs = 10000

    def log_decision(self, user_id: str, decision: str, details: Dict[str, Any]) -> Dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "decision": decision,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._logs.append(entry)
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)
        return entry

    def log_access(self, user_id: str, resource: str, action: str, status: str = "granted") -> Dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._logs.append(entry)
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)
        return entry

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._logs[-limit:]

    def search(self, user_id: Optional[str] = None, resource: Optional[str] = None) -> List[Dict[str, Any]]:
        results = self._logs
        if user_id:
            results = [e for e in results if e.get("user_id") == user_id]
        if resource:
            results = [e for e in results if e.get("resource") == resource]
        return results

    def clear(self) -> None:
        self._logs.clear()
