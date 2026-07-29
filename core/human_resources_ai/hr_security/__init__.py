"""
HR Security - Security for the HR AI Engine.
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

from ..hr_config import HRConfig
from .access_control import AccessControl
from .employee_privacy import EmployeePrivacy
from .encryption import EncryptionManager
from .audit import AuditTrail

logger = logging.getLogger(__name__)


class HRSecurityManager:
    def __init__(self, config=None):
        self._config = config or HRConfig()
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._access_ctrl = AccessControl(self._config)
        self._employee_privacy = EmployeePrivacy(self._config)
        self._encryption = EncryptionManager(self._config)
        self._audit_trail = AuditTrail(self._config)
        self._roles: Dict[str, Set[str]] = {
            "hr_director": {"read", "write", "approve", "configure", "audit", "manage_salary"},
            "hr_manager": {"read", "write", "approve", "configure"},
            "recruiter": {"read", "write", "screen", "interview"},
            "trainer": {"read", "write", "training"},
            "manager": {"read", "evaluate", "feedback"},
            "employee": {"read_own", "feedback"},
            "auditor": {"read", "audit"},
            "viewer": {"read"},
        }
        self._permissions: Dict[str, Dict[str, Set[str]]] = {}

    @property
    def access_control(self) -> AccessControl:
        return self._access_ctrl

    @property
    def employee_privacy(self) -> EmployeePrivacy:
        return self._employee_privacy

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
        sensitive = {"salary", "tax_id", "bank_account", "health_info", "evaluation", "performance_score", "bonus"}
        encrypted = {}
        for k, v in data.items():
            if k in sensitive and isinstance(v, (int, float, str)):
                encrypted[k] = base64.b64encode(self._cipher.encrypt(str(v).encode())).decode()
            else:
                encrypted[k] = v
        return encrypted

    def decrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {"salary", "tax_id", "bank_account", "health_info", "evaluation", "performance_score", "bonus"}
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
            "employee_privacy": True,
            "audit_trail": True,
            "roles": list(self._roles.keys()),
        }


__all__ = [
    "HRSecurityManager",
    "AccessControl",
    "EmployeePrivacy",
    "EncryptionManager",
    "AuditTrail",
]
