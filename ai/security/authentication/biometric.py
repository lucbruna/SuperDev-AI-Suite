"""Biometric authentication support."""
from __future__ import annotations

from typing import Any


class BiometricAuth:
    def __init__(self) -> None:
        self._enrolled: dict[str, dict[str, Any]] = {}
    def enroll(self, user_id: str, biometric_type: str = "fingerprint") -> dict[str, Any]:
        self._enrolled[user_id] = {"type": biometric_type, "enrolled": True}
        return {"user_id": user_id, "type": biometric_type, "status": "enrolled"}
    def verify(self, user_id: str, biometric_data: dict[str, Any]) -> dict[str, Any]:
        enrolled = self._enrolled.get(user_id)
        if not enrolled:
            return {"verified": False, "error": "not_enrolled"}
        return {"verified": True, "user_id": user_id, "type": enrolled["type"]}
    def revoke(self, user_id: str) -> bool:
        if user_id in self._enrolled:
            del self._enrolled[user_id]
            return True
        return False
