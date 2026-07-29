"""
Legal Security - Security for the Legal AI Engine.
"""

from __future__ import annotations

import hashlib
import logging
import base64
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from cryptography.fernet import Fernet

from ..legal_config import LegalConfig
from .access_control import AccessControl
from .document_encryption import DocumentEncryption
from .confidentiality import ConfidentialityManager
from .audit_access import AuditAccess

logger = logging.getLogger(__name__)


class LegalSecurityManager:
    def __init__(self, config=None):
        self._config = config or LegalConfig()
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._access_ctrl = AccessControl(self._config)
        self._doc_encryption = DocumentEncryption(self._config)
        self._confidentiality = ConfidentialityManager(self._config)
        self._audit_access = AuditAccess(self._config)
        self._roles: Dict[str, Set[str]] = {
            "legal_director": {"read", "write", "approve", "configure", "audit", "manage_confidential"},
            "legal_manager": {"read", "write", "approve", "configure"},
            "lawyer": {"read", "write", "analyze", "review"},
            "compliance_officer": {"read", "write", "audit", "check"},
            "paralegal": {"read", "write", "organize"},
            "auditor": {"read", "audit"},
            "viewer": {"read"},
        }
        self._permissions: Dict[str, Dict[str, Set[str]]] = {}

    @property
    def access_control(self) -> AccessControl:
        return self._access_ctrl

    @property
    def document_encryption(self) -> DocumentEncryption:
        return self._doc_encryption

    @property
    def confidentiality(self) -> ConfidentialityManager:
        return self._confidentiality

    @property
    def audit_access(self) -> AuditAccess:
        return self._audit_access

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
        sensitive = {"contract_value", "tax_id", "legal_opinion", "evidence", "salary", "confidential_note"}
        encrypted = {}
        for k, v in data.items():
            if k in sensitive and isinstance(v, (int, float, str)):
                encrypted[k] = base64.b64encode(self._cipher.encrypt(str(v).encode())).decode()
            else:
                encrypted[k] = v
        return encrypted

    def decrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {"contract_value", "tax_id", "legal_opinion", "evidence", "salary", "confidential_note"}
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
            "confidentiality": True,
            "audit_trail": True,
            "roles": list(self._roles.keys()),
        }


__all__ = [
    "LegalSecurityManager",
    "AccessControl",
    "DocumentEncryption",
    "ConfidentialityManager",
    "AuditAccess",
]
