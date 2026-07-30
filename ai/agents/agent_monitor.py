from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .agent_state import AgentState


class AgentMonitor:
    """Monitors agent health and status."""

    def __init__(self) -> None:
        self._heartbeats: Dict[str, float] = {}
        self._timeout: float = 30.0

    def heartbeat(self, agent_id: str) -> None:
        self._heartbeats[agent_id] = time.time()

    def is_alive(self, agent_id: str) -> bool:
        last = self._heartbeats.get(agent_id)
        if last is None:
            return False
        return (time.time() - last) < self._timeout

    def alive_agents(self) -> List[str]:
        return [aid for aid in self._heartbeats if self.is_alive(aid)]

    def dead_agents(self) -> List[str]:
        return [aid for aid in self._heartbeats if not self.is_alive(aid)]

    def clear(self) -> None:
        self._heartbeats.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "alive": len(self.alive_agents()),
            "dead": len(self.dead_agents()),
            "total": len(self._heartbeats),
        }
