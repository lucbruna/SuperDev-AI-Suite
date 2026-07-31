"""Access control over knowledge items."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_models import AccessLevel
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity

_ACCESS_ORDER = {"public": 0, "internal": 1, "confidential": 2,
                 "restricted": 3}


class AccessControl:
    """Decides whether an actor may view an item."""

    def __init__(self, security: EnterpriseKnowledgeSecurity | None = None) -> None:
        self.security = security or EnterpriseKnowledgeSecurity()

    def allowed(self, role: str, item_access: AccessLevel,
                actor_level: AccessLevel | None = None) -> bool:
        level = actor_level or self.security.role_level(role)
        return _ACCESS_ORDER[level.value] >= _ACCESS_ORDER[item_access.value]

    def required_level(self, item_access: AccessLevel) -> AccessLevel:
        return item_access

    @staticmethod
    def classify_rank(item_access: AccessLevel) -> int:
        return _ACCESS_ORDER[item_access.value]

    @staticmethod
    def role_rank(role: str) -> int:
        return _ACCESS_ORDER[EnterpriseKnowledgeSecurity().role_level(role).value]
