from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from ..physical_config import PhysicalConfig

logger = logging.getLogger(__name__)


class AccessControl:
    def __init__(self, config: PhysicalConfig):
        self._config = config
        self._policies: Dict[str, Set[str]] = {}

    def add_policy(self, resource: str, allowed_roles: Set[str]) -> None:
        self._policies[resource] = allowed_roles

    def check(self, user_role: str, resource: str, action: str) -> bool:
        policy = self._policies.get(resource)
        if not policy:
            return False
        return user_role in policy

    def remove_policy(self, resource: str) -> bool:
        return bool(self._policies.pop(resource, None))

    def list_policies(self) -> Dict[str, List[str]]:
        return {k: list(v) for k, v in self._policies.items()}
