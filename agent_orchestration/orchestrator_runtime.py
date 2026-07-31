"""Runtime lifecycle for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_logger import get_logger


class OrchestratorRuntime:
    """Tracks the orchestrator run state."""

    def __init__(self) -> None:
        self._log = get_logger("runtime")
        self._state = "stopped"
        self._started_at = 0.0
        self._stopped_at = 0.0

    def start(self) -> bool:
        if self._state == "running":
            return False
        self._state = "running"
        self._started_at = __import__("time").time()
        self._log.info("agent orchestration runtime started")
        return True

    def stop(self) -> bool:
        if self._state == "stopped":
            return False
        self._state = "stopped"
        self._stopped_at = __import__("time").time()
        self._log.info("agent orchestration runtime stopped")
        return True

    def is_running(self) -> bool:
        return self._state == "running"

    def state(self) -> dict[str, Any]:
        return {
            "state": self._state,
            "started_at": self._started_at,
            "stopped_at": self._stopped_at,
        }
