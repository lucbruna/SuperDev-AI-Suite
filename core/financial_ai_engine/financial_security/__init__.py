"""
Financial Security - Security for the Financial AI Engine.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import base64
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from cryptography.fernet import Fernet

from ..financial_config import FinancialConfig
from .access_control import AccessControl
from .transaction_security import TransactionSecurity
from .encryption import EncryptionManager
from .audit_trail import AuditTrail

logger = logging.getLogger(__name__)


class FinancialSecurityManager:
    def __init__(self, config=None):
        self._config = config or FinancialConfig()
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._access_ctrl = AccessControl(self._config)
        self._tx_security = TransactionSecurity(self._config)
        self._encryption = EncryptionManager(self._config)
        self._audit_trail = AuditTrail(self._config)
        self._roles: Dict[str, Set[str]] = {
            "cfi": {"read", "write", "approve", "configure", "audit"},
            "treasury": {"read", "write", "approve", "configure"},
            "accountant": {"read", "write", "reconcile"},
            "auditor": {"read", "audit"},
            "viewer": {"read"},
        }
        self._permissions: Dict[str, Dict[str, Set[str]]] = {}

    @property
    def access_control(self) -> AccessControl:
        return self._access_ctrl

    @property
    def transaction_security(self) -> TransactionSecurity:
        return self._tx_security

    @property
    def encryption(self) -> EncryptionManager:
        return self._encryption

    @property
    def audit_trail(self) -> AuditTrail:
        return self._audit_trail

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        role = self._permissions.get(user_id, {}).get("role")
        if not role:
            return False
        return action in self._roles.get(role, set())

    def set_user_role(self, user_id: str, role: str) -> None:
        if role not in self._roles:
            raise ValueError(f"Invalid role: {role}")
        if user_id not in self._permissions:
            self._permissions[user_id] = {}
        self._permissions[user_id]["role"] = role

    def encrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {"bank_account", "tax_id", "salary", "price", "cost", "commission"}
        encrypted = {}
        for k, v in data.items():
            if k in sensitive and isinstance(v, (int, float, str)):
                encrypted[k] = base64.b64encode(self._cipher.encrypt(str(v).encode())).decode()
            else:
                encrypted[k] = v
        return encrypted

    def decrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {"bank_account", "tax_id", "salary", "price", "cost", "commission"}
        decrypted = {}
        for k, v in data.items():
            if k in sensitive and isinstance(v, str):
                try:
                    decrypted[k] = self._cipher.decrypt(base64.b64decode(v)).decode()
                except Exception:
                    decrypted[k] = v
            else:
                decrypted[k] = v
        return decrypted

    def audit(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "type": transaction.get("type", "unknown"),
            "user": transaction.get("user_id", "system"),
            "resource": transaction.get("resource", "unknown"),
            "action": transaction.get("action", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "status": transaction.get("status", "success"),
        }
        return entry

    def get_security_report(self) -> Dict[str, Any]:
        return {
            "encryption_active": True,
            "access_control": True,
            "audit_trail": True,
            "roles": list(self._roles.keys()),
        }


__all__ = [
    "FinancialSecurityManager",
    "AccessControl",
    "TransactionSecurity",
    "EncryptionManager",
    "AuditTrail",
]