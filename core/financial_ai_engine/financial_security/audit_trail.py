"""
Audit Trail - Comprehensive financial audit logging.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class AuditTrail:
    def __init__(self, config: FinancialConfig):
        self.config = config
        self._log: List[Dict[str, Any]] = []
        self._max_size = 10000

    async def log(self, action: str, user_id: str, resource: str, details: Dict[str, Any],
                  status: str = "success") -> str:
        entry_id = str(uuid.uuid4())[:8]
        entry = {
            "id": entry_id, "action": action, "user_id": user_id,
            "resource": resource, "details": details,
            "status": status, "timestamp": datetime.utcnow().isoformat(),
        }
        self._log.append(entry)
        if len(self._log) > self._max_size:
            self._log.pop(0)
        logger.info(f"Audit: {user_id} -> {action} on {resource}")
        return entry_id

    async def query(self, user_id: Optional[str] = None, resource: Optional[str] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        results = self._log
        if user_id:
            results = [e for e in results if e["user_id"] == user_id]
        if resource:
            results = [e for e in results if e["resource"] == resource]
        return results[-limit:]

    async def generate_report(self) -> Dict[str, Any]:
        return {
            "total_entries": len(self._log),
            "by_action": {},
            "by_user": {},
        }