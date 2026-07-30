from __future__ import annotations

from typing import Any, Dict, List, Optional

from .agent_engine import AgentEngine


class AgentManager:
    """Manages agent lifecycle and operations."""

    def __init__(self, engine: AgentEngine) -> None:
        self._engine = engine

    @property
    def engine(self) -> AgentEngine:
        return self._engine

    def start_all(self) -> None:
        self._engine.start()

    def stop_all(self) -> None:
        self._engine.stop()

    def get_agent_ids(self) -> List[str]:
        return self._engine.registry.agent_ids

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        agent = self._engine.registry.get_agent(agent_id)
        return agent.to_dict() if agent else None

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        agent_id = self._engine.route_task(task)
        if agent_id is None:
            return {"status": "error", "message": "No agent found for task"}
        return self._engine.dispatch(agent_id, task)

    def snapshot(self) -> Dict[str, Any]:
        return self._engine.snapshot()
