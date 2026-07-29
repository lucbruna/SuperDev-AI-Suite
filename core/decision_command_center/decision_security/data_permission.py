from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class DataPermission:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._permissions: Dict[str, Set[str]] = {}

    def grant(self, user_id: str, category: str) -> None:
        if user_id not in self._permissions:
            self._permissions[user_id] = set()
        self._permissions[user_id].add(category)

    def revoke(self, user_id: str, category: str) -> None:
        if user_id in self._permissions:
            self._permissions[user_id].discard(category)

    def can_access(self, user_id: str, category: str) -> bool:
        return user_id in self._permissions and category in self._permissions[user_id]

    def get_user_categories(self, user_id: str) -> Set[str]:
        return self._permissions.get(user_id, set())

    def list_all(self) -> Dict[str, List[str]]:
        return {k: list(v) for k, v in self._permissions.items()}
