"""
Audit Trail - Audit logging for HR systems.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class AuditTrail:
    def __init__(self, config: HRConfig):
        self.config = config
        self._entries: List[Dict[str, Any]] = []
        self._max_entries = 10000

    def log(self, action: str, user_id: str, resource: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries.pop(0)
        return entry

    def query(self, user_id: Optional[str] = None, action: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        results = self._entries
        if user_id:
            results = [e for e in results if e["user_id"] == user_id]
        if action:
            results = [e for e in results if e["action"] == action]
        return results[-limit:]
