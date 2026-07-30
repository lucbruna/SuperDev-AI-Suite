from __future__ import annotations

from typing import Any, Dict, List, Optional


class AgentPermissions:
    """Manages permissions for agent actions."""

    def __init__(self) -> None:
        self._permissions: Dict[str, List[str]] = {}

    def grant(self, agent_id: str, action: str) -> None:
        if agent_id not in self._permissions:
            self._permissions[agent_id] = []
        self._permissions[agent_id].append(action)

    def revoke(self, agent_id: str, action: str) -> bool:
        actions = self._permissions.get(agent_id)
        if actions and action in actions:
            actions.remove(action)
            return True
        return False

    def check(self, agent_id: str, action: str) -> bool:
        actions = self._permissions.get(agent_id)
        return actions is not None and action in actions

    def revoke_all(self, agent_id: str) -> bool:
        return self._permissions.pop(agent_id, None) is not None

    def clear(self) -> None:
        self._permissions.clear()

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._permissions)
