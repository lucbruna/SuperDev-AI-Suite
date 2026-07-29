"""
Supply Chain Security - Security and access control for the supply chain engine.

Provides access control, data encryption, transaction auditing,
and protection of sensitive supply chain data.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import base64
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from cryptography.fernet import Fernet

from ..supply_config import SupplyChainConfig
from .access_control import AccessControl
from .supplier_data_protection import SupplierDataProtection
from .transaction_audit import TransactionAudit
from .security_monitor import SecurityMonitor

logger = logging.getLogger(__name__)


@dataclass
class AccessControlEntry:
    user_id: str
    resource: str
    actions: Set[str]
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class AuditEntry:
    id: str
    transaction_type: str
    user_id: str
    resource: str
    action: str
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str] = None
    status: str = "success"


class SupplySecurityManager:
    def __init__(self, config=None):
        self._config = config or SupplyChainConfig()
        self._access_controls: List[AccessControlEntry] = []
        self._audit_log: List[AuditEntry] = []
        self._max_audit_size = 10000
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._roles: Dict[str, Set[str]] = self._init_roles()
        self._permissions: Dict[str, Dict[str, Set[str]]] = {}
        self._access_ctrl = AccessControl(self._config)
        self._data_protection = SupplierDataProtection(self._config)
        self._audit = TransactionAudit(self._config)
        self._security_monitor = SecurityMonitor(self._config)

    @property
    def access_control(self) -> AccessControl:
        return self._access_ctrl

    @property
    def data_protection(self) -> SupplierDataProtection:
        return self._data_protection

    @property
    def transaction_audit(self) -> TransactionAudit:
        return self._audit

    @property
    def security_monitor(self) -> SecurityMonitor:
        return self._security_monitor

    def _init_roles(self) -> Dict[str, Set[str]]:
        return {
            "admin": {"read", "write", "delete", "approve", "configure", "audit"},
            "manager": {"read", "write", "approve", "configure"},
            "analyst": {"read"},
            "buyer": {"read", "write", "approve"},
            "viewer": {"read"},
            "auditor": {"read", "audit"},
        }

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        role = self._get_user_role(user_id)
        if not role:
            return False
        allowed_actions = self._roles.get(role, set())
        return action in allowed_actions

    def grant_access(self, user_id: str, resource: str, actions: Set[str], granted_by: str) -> AccessControlEntry:
        entry = AccessControlEntry(
            user_id=user_id,
            resource=resource,
            actions=actions,
            granted_by=granted_by,
            granted_at=datetime.utcnow(),
        )
        self._access_controls.append(entry)
        logger.info(f"Access granted: {user_id} -> {actions} on {resource}")
        return entry

    def revoke_access(self, user_id: str, resource: str) -> bool:
        remaining = [ace for ace in self._access_controls if not (ace.user_id == user_id and ace.resource == resource)]
        revoked = len(remaining) < len(self._access_controls)
        self._access_controls = remaining
        if revoked:
            logger.info(f"Access revoked: {user_id} -> {resource}")
        return revoked

    def get_user_permissions(self, user_id: str) -> Dict[str, Set[str]]:
        return {
            ace.resource: ace.actions
            for ace in self._access_controls
            if ace.user_id == user_id
        }

    def audit(self, transaction: Dict[str, Any]) -> AuditEntry:
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            transaction_type=transaction.get("type", "unknown"),
            user_id=transaction.get("user_id", "system"),
            resource=transaction.get("resource", "unknown"),
            action=transaction.get("action", "unknown"),
            details=transaction.get("details", {}),
            timestamp=datetime.utcnow(),
            ip_address=transaction.get("ip_address"),
            status=transaction.get("status", "success"),
        )
        self._audit_log.append(entry)
        if len(self._audit_log) > self._max_audit_size:
            self._audit_log.pop(0)
        return entry

    def get_audit_log(self, resource: Optional[str] = None, user_id: Optional[str] = None, limit: int = 100) -> List[AuditEntry]:
        results = self._audit_log
        if resource:
            results = [e for e in results if e.resource == resource]
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        return results[-limit:]

    def encrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive_fields = {"price", "cost", "discount", "contract_value", "margin", "negotiated_price"}
        encrypted = {}
        for key, value in data.items():
            if key in sensitive_fields and isinstance(value, (int, float, str)):
                plaintext = str(value).encode()
                encrypted[key] = base64.b64encode(self._cipher.encrypt(plaintext)).decode()
            else:
                encrypted[key] = value
        return encrypted

    def decrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive_fields = {"price", "cost", "discount", "contract_value", "margin", "negotiated_price"}
        decrypted = {}
        for key, value in data.items():
            if key in sensitive_fields and isinstance(value, str):
                try:
                    ciphertext = base64.b64decode(value)
                    decrypted[key] = self._cipher.decrypt(ciphertext).decode()
                except Exception:
                    decrypted[key] = value
            else:
                decrypted[key] = value
        return decrypted

    def hash_sensitive_id(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()[:16]

    def validate_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def _get_user_role(self, user_id: str) -> Optional[str]:
        return self._permissions.get(user_id, {}).get("role")

    def set_user_role(self, user_id: str, role: str) -> None:
        if role not in self._roles:
            raise ValueError(f"Invalid role: {role}")
        if user_id not in self._permissions:
            self._permissions[user_id] = {}
        self._permissions[user_id]["role"] = role
        logger.info(f"Role set: {user_id} -> {role}")

    def get_security_report(self) -> Dict[str, Any]:
        return {
            "active_controls": len(self._access_controls),
            "audit_entries": len(self._audit_log),
            "roles_defined": list(self._roles.keys()),
            "users_with_permissions": len(self._permissions),
            "encryption_active": True,
            "last_audit": self._audit_log[-1].timestamp if self._audit_log else None,
        }


__all__ = [
    "SupplySecurityManager",
    "AccessControlEntry",
    "AuditEntry",
    "AccessControl",
    "SupplierDataProtection",
    "TransactionAudit",
    "SecurityMonitor",
]