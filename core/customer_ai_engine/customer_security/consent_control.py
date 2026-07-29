"""
Consent Control - Manage customer consent for data processing.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class ConsentControl:
    def __init__(self, config: CustomerConfig):
        self.config = config
        self._consents: Dict[str, Dict[str, Any]] = {}

    def register_consent(self, customer_id: str, purpose: str, granted: bool = True) -> Dict[str, Any]:
        record = {
            "customer_id": customer_id,
            "purpose": purpose,
            "granted": granted,
            "granted_at": datetime.utcnow().isoformat() if granted else None,
            "revoked_at": None if granted else datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4()),
        }
        key = f"{customer_id}:{purpose}"
        self._consents[key] = record
        return record

    def check(self, customer_id: str, purpose: str) -> bool:
        key = f"{customer_id}:{purpose}"
        record = self._consents.get(key)
        if record is None:
            return False
        return record.get("granted", False) and record.get("revoked_at") is None

    def revoke_consent(self, customer_id: str, purpose: str) -> bool:
        key = f"{customer_id}:{purpose}"
        record = self._consents.get(key)
        if record is None:
            return False
        record["granted"] = False
        record["revoked_at"] = datetime.utcnow().isoformat()
        return True

    def list_consents(self, customer_id: str) -> List[Dict[str, Any]]:
        return [v for k, v in self._consents.items() if k.startswith(f"{customer_id}:")]

    def get_consent_summary(self, customer_id: str) -> Dict[str, Any]:
        consents = self.list_consents(customer_id)
        return {
            "customer_id": customer_id,
            "total": len(consents),
            "granted": sum(1 for c in consents if c["granted"]),
            "revoked": sum(1 for c in consents if not c["granted"]),
            "purposes": [c["purpose"] for c in consents if c["granted"]],
        }
