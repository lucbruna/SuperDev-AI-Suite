"""
Audit Access - Track and audit document access.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..legal_config import LegalConfig

logger = logging.getLogger(__name__)


class AuditAccess:
    def __init__(self, config: LegalConfig):
        self.config = config
        self._logs: List[Dict[str, Any]] = []
        self._max_logs = 10000

    def log_access(self, user_id: str, document_id: str, action: str, status: str = "granted") -> Dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "document_id": document_id,
            "action": action,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._logs.append(entry)
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)
        return entry

    def query(self, user_id: Optional[str] = None, document_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        results = self._logs
        if user_id:
            results = [r for r in results if r["user_id"] == user_id]
        if document_id:
            results = [r for r in results if r["document_id"] == document_id]
        return results[-limit:]
