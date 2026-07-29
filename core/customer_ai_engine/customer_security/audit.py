"""
Audit Manager - Track and audit customer data access.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class AuditManager:
    def __init__(self, config: CustomerConfig):
        self.config = config
        self._logs: List[Dict[str, Any]] = []
        self._max_logs = 10000

    def log_access(self, user_id: str, resource: str, action: str, status: str = "granted") -> Dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": "0.0.0.0",
        }
        self._logs.append(entry)
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)
        return entry

    def query(self, user_id: Optional[str] = None, resource: Optional[str] = None,
              action: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        results = self._logs
        if user_id:
            results = [r for r in results if r["user_id"] == user_id]
        if resource:
            results = [r for r in results if r["resource"] == resource]
        if action:
            results = [r for r in results if r["action"] == action]
        return results[-limit:]

    def get_recent_activity(self, minutes: int = 60) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow().timestamp() - minutes * 60
        return [r for r in self._logs if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff]
