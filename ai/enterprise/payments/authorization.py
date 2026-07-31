"""Payment authorization."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class PaymentAuthorization:
    def __init__(self) -> None:
        self._authorizations: Dict[str, Dict[str, Any]] = {}
    def authorize(self, payment_id: str, amount: float) -> Dict[str, Any]:
        auth = {"payment_id": payment_id, "amount": amount, "status": "authorized", "authorized_at": time.time(), "expires_at": time.time() + 900}
        self._authorizations[payment_id] = auth
        return auth
    def capture(self, payment_id: str) -> bool:
        auth = self._authorizations.get(payment_id)
        if auth:
            auth["status"] = "captured"
            auth["captured_at"] = time.time()
            return True
        return False
    def void(self, payment_id: str) -> bool:
        auth = self._authorizations.get(payment_id)
        if auth:
            auth["status"] = "voided"
            return True
        return False
    def is_authorized(self, payment_id: str) -> bool:
        auth = self._authorizations.get(payment_id)
        return auth is not None and auth["status"] == "authorized"
    def is_expired(self, payment_id: str) -> bool:
        auth = self._authorizations.get(payment_id)
        if not auth:
            return True
        return time.time() > auth.get("expires_at", 0)
    def get(self, payment_id: str) -> Dict[str, Any]:
        return self._authorizations.get(payment_id, {})
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._authorizations.values())
