from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from cryptography.fernet import Fernet

from ..decision_config import DecisionConfig
from .access_policy import AccessPolicy
from .data_permission import DataPermission
from .approval_manager import ApprovalManager
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

DECISION_ROLES: Dict[str, Set[str]] = {
    "ceo": {"read", "write", "approve", "configure", "audit", "delete", "manage_users", "strategic_decisions"},
    "director": {"read", "write", "approve", "configure", "audit", "strategic_decisions"},
    "manager": {"read", "write", "approve", "configure"},
    "analyst": {"read", "write", "analyze", "simulate"},
    "advisor": {"read", "analyze", "recommend"},
    "viewer": {"read"},
    "auditor": {"read", "audit"},
}


class DecisionSecurityManager:
    def __init__(self, config=None):
        self._config = config or DecisionConfig()
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._access = AccessPolicy(self._config)
        self._permissions = DataPermission(self._config)
        self._approvals = ApprovalManager(self._config)
        self._audit = AuditLogger(self._config)
        self._roles: Dict[str, str] = {}

    @property
    def access(self) -> AccessPolicy:
        return self._access

    @property
    def permissions(self) -> DataPermission:
        return self._permissions

    @property
    def approvals(self) -> ApprovalManager:
        return self._approvals

    @property
    def audit(self) -> AuditLogger:
        return self._audit

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        role = self._roles.get(user_id)
        if not role:
            return False
        return action in DECISION_ROLES.get(role, set())

    def set_user_role(self, user_id: str, role: str) -> None:
        if role not in DECISION_ROLES:
            raise ValueError(f"Invalid role: {role}")
        self._roles[user_id] = role

    def encrypt_strategic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {"strategy", "financial_forecast", "acquisition_plan", "competitive_intel"}
        encrypted = {}
        for k, v in data.items():
            if k in sensitive and isinstance(v, (int, float, str)):
                encrypted[k] = self._cipher.encrypt(str(v).encode()).decode()
            else:
                encrypted[k] = v
        return encrypted

    def decrypt_strategic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {"strategy", "financial_forecast", "acquisition_plan", "competitive_intel"}
        decrypted = {}
        for k, v in data.items():
            if k in sensitive and isinstance(v, str):
                try:
                    decrypted[k] = self._cipher.decrypt(v.encode()).decode()
                except Exception:
                    decrypted[k] = v
            else:
                decrypted[k] = v
        return decrypted

    def log_decision(self, user_id: str, decision: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return self._audit.log_decision(user_id, decision, details)

    def require_approval(self, decision_type: str, value: float) -> bool:
        return self._approvals.require_approval(decision_type, value)

    def approve_decision(self, decision_id: str, approver_id: str) -> Dict[str, Any]:
        return self._approvals.approve(decision_id, approver_id)

    def can_access_data(self, user_id: str, data_category: str) -> bool:
        return self._permissions.can_access(user_id, data_category)

    def get_security_report(self) -> Dict[str, Any]:
        return {
            "encryption_active": True,
            "access_control": True,
            "approval_workflow": True,
            "audit_trail": True,
            "roles": list(DECISION_ROLES.keys()),
            "data_permissions": True,
        }


__all__ = [
    "DecisionSecurityManager",
    "AccessPolicy",
    "DataPermission",
    "ApprovalManager",
    "AuditLogger",
]
