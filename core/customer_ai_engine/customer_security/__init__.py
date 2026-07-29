"""
Customer Security - Security for the Customer AI Engine.
"""

from __future__ import annotations

import hashlib
import logging
import base64
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from cryptography.fernet import Fernet

from ..customer_config import CustomerConfig
from .privacy_manager import PrivacyManager
from .consent_control import ConsentControl
from .data_protection import DataProtection
from .audit import AuditManager

logger = logging.getLogger(__name__)


class CustomerSecurityManager:
    def __init__(self, config=None):
        self._config = config or CustomerConfig()
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._privacy = PrivacyManager(self._config)
        self._consent = ConsentControl(self._config)
        self._data_protection = DataProtection(self._config)
        self._audit = AuditManager(self._config)
        self._roles: Dict[str, Set[str]] = {
            "cx_director": {"read", "write", "approve", "configure", "audit", "manage_privacy"},
            "cx_manager": {"read", "write", "approve", "configure"},
            "agent": {"read", "write", "respond", "escalate"},
            "analyst": {"read", "analyze"},
            "auditor": {"read", "audit"},
            "viewer": {"read"},
        }
        self._permissions: Dict[str, Dict[str, Set[str]]] = {}

    @property
    def privacy(self) -> PrivacyManager:
        return self._privacy

    @property
    def consent(self) -> ConsentControl:
        return self._consent

    @property
    def data_protection(self) -> DataProtection:
        return self._data_protection

    @property
    def audit(self) -> AuditManager:
        return self._audit

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

    def encrypt_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pii_fields = {"phone", "email", "address", "payment_info", "cpf", "credit_card"}
        encrypted = {}
        for k, v in data.items():
            if k in pii_fields and isinstance(v, (int, float, str)):
                encrypted[k] = base64.b64encode(self._cipher.encrypt(str(v).encode())).decode()
            else:
                encrypted[k] = v
        return encrypted

    def decrypt_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pii_fields = {"phone", "email", "address", "payment_info", "cpf", "credit_card"}
        decrypted = {}
        for k, v in data.items():
            if k in pii_fields and isinstance(v, str):
                try:
                    decrypted[k] = self._cipher.decrypt(base64.b64decode(v)).decode()
                except Exception:
                    decrypted[k] = v
            else:
                decrypted[k] = v
        return decrypted

    def log_access(self, user_id: str, resource: str, action: str, status: str = "granted") -> Dict[str, Any]:
        return self._audit.log_access(user_id, resource, action, status)

    def check_consent(self, customer_id: str, purpose: str) -> bool:
        return self._consent.check(customer_id, purpose)

    def anonymize_customer(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return self._privacy.anonymize(profile)

    def get_security_report(self) -> Dict[str, Any]:
        return {
            "encryption_active": True,
            "access_control": True,
            "privacy_protection": True,
            "consent_management": True,
            "audit_trail": True,
            "roles": list(self._roles.keys()),
        }


__all__ = [
    "CustomerSecurityManager",
    "PrivacyManager",
    "ConsentControl",
    "DataProtection",
    "AuditManager",
]
