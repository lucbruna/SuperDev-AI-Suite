from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class ApprovalManager:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._pending: Dict[str, Dict[str, Any]] = {}

    def require_approval(self, decision_type: str, value: float) -> bool:
        thresholds = {
            "budget": 50000.0,
            "hiring": 0,
            "acquisition": 100000.0,
            "strategy_change": 0,
        }
        threshold = thresholds.get(decision_type, float("inf"))
        return value > threshold

    def submit(self, decision_type: str, details: Dict[str, Any]) -> str:
        approval_id = str(uuid.uuid4())
        self._pending[approval_id] = {
            "id": approval_id,
            "decision_type": decision_type,
            "details": details,
            "status": "pending",
            "submitted_at": datetime.utcnow(),
            "approved_by": None,
            "approved_at": None,
        }
        return approval_id

    def approve(self, approval_id: str, approver_id: str) -> Dict[str, Any]:
        entry = self._pending.get(approval_id)
        if not entry:
            raise ValueError(f"Approval not found: {approval_id}")
        entry["status"] = "approved"
        entry["approved_by"] = approver_id
        entry["approved_at"] = datetime.utcnow()
        return entry

    def reject(self, approval_id: str, reason: str = "") -> Dict[str, Any]:
        entry = self._pending.get(approval_id)
        if not entry:
            raise ValueError(f"Approval not found: {approval_id}")
        entry["status"] = "rejected"
        entry["reason"] = reason
        return entry

    def get_pending(self) -> List[Dict[str, Any]]:
        return [e for e in self._pending.values() if e["status"] == "pending"]

    def get_status(self, approval_id: str) -> Optional[str]:
        entry = self._pending.get(approval_id)
        return entry["status"] if entry else None
