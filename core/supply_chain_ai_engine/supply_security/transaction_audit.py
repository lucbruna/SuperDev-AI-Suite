"""
Transaction Audit - Comprehensive audit logging for supply chain transactions.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class TransactionAudit:
    def __init__(self, config: SupplyChainConfig):
        self.config = config
        self._log: List[Dict[str, Any]] = []
        self._max_size = 10000

    async def log(self, transaction_type: str, user_id: str, resource: str, action: str,
                  details: Dict[str, Any], status: str = "success") -> str:
        entry_id = str(uuid.uuid4())[:8]
        entry = {
            "id": entry_id,
            "type": transaction_type,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "details": details,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._log.append(entry)
        if len(self._log) > self._max_size:
            self._log.pop(0)
        logger.info(f"Audit: {user_id} -> {action} on {resource} ({status})")
        return entry_id

    async def query(self, resource: Optional[str] = None, user_id: Optional[str] = None,
                    transaction_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        results = self._log
        if resource:
            results = [e for e in results if e["resource"] == resource]
        if user_id:
            results = [e for e in results if e["user_id"] == user_id]
        if transaction_type:
            results = [e for e in results if e["type"] == transaction_type]
        return results[-limit:]

    async def generate_report(self, days: int = 30) -> Dict[str, Any]:
        cutoff = datetime.utcnow()
        recent = [e for e in self._log if e["timestamp"] >= cutoff.isoformat()]
        return {
            "total_transactions": len(recent),
            "success_rate": sum(1 for e in recent if e["status"] == "success") / max(len(recent), 1),
            "by_type": {},
            "by_user": {},
        }