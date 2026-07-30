from __future__ import annotations

from typing import Any, Dict, List


class Multicast:
    """Multicasts messages to a group of agents."""

    def __init__(self) -> None:
        self._groups: Dict[str, List[str]] = {}

    def create_group(self, group: str) -> None:
        if group not in self._groups:
            self._groups[group] = []

    def join(self, group: str, agent_id: str) -> None:
        if group in self._groups and agent_id not in self._groups[group]:
            self._groups[group].append(agent_id)

    def leave(self, group: str, agent_id: str) -> bool:
        if group in self._groups and agent_id in self._groups[group]:
            self._groups[group].remove(agent_id)
            return True
        return False

    def send(self, sender: str, group: str, content: Dict[str, Any]) -> int:
        recipients = self._groups.get(group, [])
        return len(recipients)

    def group_members(self, group: str) -> List[str]:
        return list(self._groups.get(group, []))

    def to_dict(self) -> Dict[str, Any]:
        return {"groups": {g: list(m) for g, m in self._groups.items()}}
