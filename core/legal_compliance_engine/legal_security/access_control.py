"""
Access Control - Role-based access control for legal systems.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from ..legal_config import LegalConfig

logger = logging.getLogger(__name__)


class AccessControl:
    def __init__(self, config: LegalConfig):
        self.config = config
        self._policies: Dict[str, Set[str]] = {}

    def grant(self, user_id: str, resource: str, action: str) -> None:
        if user_id not in self._policies:
            self._policies[user_id] = set()
        self._policies[user_id].add(f"{resource}:{action}")

    def revoke(self, user_id: str, resource: str, action: str) -> None:
        key = f"{resource}:{action}"
        if user_id in self._policies and key in self._policies[user_id]:
            self._policies[user_id].remove(key)

    def check(self, user_id: str, resource: str, action: str) -> bool:
        return user_id in self._policies and f"{resource}:{action}" in self._policies[user_id]
