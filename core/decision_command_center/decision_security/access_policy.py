from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class AccessPolicy:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._policies: Dict[str, Dict[str, Any]] = {}

    def add_policy(self, resource: str, allowed_roles: Set[str], conditions: Optional[Dict[str, Any]] = None) -> None:
        self._policies[resource] = {
            "allowed_roles": allowed_roles,
            "conditions": conditions or {},
        }

    def check(self, user_role: str, resource: str, action: str) -> bool:
        policy = self._policies.get(resource)
        if not policy:
            return False
        return user_role in policy["allowed_roles"]

    def remove_policy(self, resource: str) -> bool:
        return bool(self._policies.pop(resource, None))

    def list_policies(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._policies)
