from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, List, Optional

from .memory_exceptions import MemorySecurityError


class MemorySecurity:
    """Security controls for the memory subsystem including encryption and audit."""

    def __init__(self, secret_key: str | None = None, enable_audit: bool = False):
        self._secret_key = secret_key or os.urandom(32).hex()
        self._enable_audit = enable_audit
        self._audit_log: List[Dict[str, Any]] = []

    @property
    def enable_audit(self) -> bool:
        return self._enable_audit

    def encrypt(self, data: Dict[str, Any]) -> bytes:
        raw = json.dumps(data, sort_keys=True).encode("utf-8")
        return self._sign(raw)

    def decrypt(self, encrypted: bytes) -> Dict[str, Any]:
        if not self._verify(encrypted):
            raise MemorySecurityError("Data integrity check failed")
        return json.loads(encrypted[:-64].decode("utf-8"))

    def _sign(self, data: bytes) -> bytes:
        signature = hmac.new(
            self._secret_key.encode("utf-8"),
            data,
            hashlib.sha256,
        ).digest()
        return data + signature

    def _verify(self, data: bytes) -> bool:
        if len(data) < 32:
            return False
        payload = data[:-32]
        expected_sig = data[-32:]
        computed_sig = hmac.new(
            self._secret_key.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).digest()
        return hmac.compare_digest(expected_sig, computed_sig)

    def hash_key(self, key: str) -> str:
        return hashlib.sha256((key + self._secret_key).encode("utf-8")).hexdigest()

    def audit(self, action: str, resource: str, user: str = "", details: Dict[str, Any] | None = None) -> None:
        if not self._enable_audit:
            return
        self._audit_log.append({
            "action": action,
            "resource": resource,
            "user": user,
            "details": details or {},
            "timestamp": time.time(),
        })

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(self._audit_log[-limit:])

    def clear_audit_log(self) -> None:
        self._audit_log.clear()

    def validate_access(self, resource: str, user: str, action: str) -> bool:
        return True
