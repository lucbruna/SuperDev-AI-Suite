from __future__ import annotations

from typing import Any, Dict, List, Optional

from .agent_registry import AgentRegistry
from .agent_router import AgentRouter
from .agent_dispatcher import AgentDispatcher


class AgentEngine:
    """Central agents orchestrator."""

    def __init__(self) -> None:
        self._registry = AgentRegistry()
        self._router = AgentRouter()
        self._dispatcher = AgentDispatcher()
        self._running: bool = False

    @property
    def registry(self) -> AgentRegistry:
        return self._registry

    @property
    def router(self) -> AgentRouter:
        return self._router

    @property
    def dispatcher(self) -> AgentDispatcher:
        return self._dispatcher

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def route_task(self, task: Dict[str, Any]) -> Optional[str]:
        return self._router.route(task, self._registry)

    def dispatch(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        return self._dispatcher.dispatch(agent_id, task)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "agents": self._registry.agent_count,
            "routes": self._router.route_count,
        }
