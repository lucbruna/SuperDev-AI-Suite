from __future__ import annotations

from typing import Any, Dict, List, Set


class AgentPermissions:
    """Permissions for agent base operations."""

    def __init__(self) -> None:
        self._allowed_actions: Set[str] = set()

    def allow(self, action: str) -> None:
        self._allowed_actions.add(action)

    def deny(self, action: str) -> bool:
        return self._allowed_actions.discard(action) is None

    def can(self, action: str) -> bool:
        return action in self._allowed_actions

    def allowed_actions(self) -> List[str]:
        return sorted(self._allowed_actions)

    def clear(self) -> None:
        self._allowed_actions.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {"allowed_actions": self.allowed_actions()}
