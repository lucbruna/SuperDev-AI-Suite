"""AI Agent Orchestration Engine - Central Coordinator.

Volume 13 of SuperDev AI Suite v5 Enterprise.
Manages the full agent lifecycle: creation, communication, collaboration,
memory, planning, reasoning, execution, evaluation, learning, and optimization.
"""

from __future__ import annotations

import time
from typing import Any

from .agent_config import AgentConfig, OrchestrationConfig, TeamConfig
from .agent_dispatcher import AgentDispatcher
from .agent_events import AgentEvents
from .agent_logger import AgentLogger
from .agent_metrics import AgentMetrics
from .agent_registry import AgentRegistry
from .agent_router import AgentRouter
from .agent_security import AgentSecurity


class AgentEngine:
    """Central AI Agent Orchestration Engine.

    Orchestrates a hierarchy of specialized agents:
    Level 0: Super Orchestrator
    Level 1: Domain Managers
    Level 2: Specialists
    Level 3: Executors
    Level 4: Tools

    Manages creation, registration, communication, delegation,
    memory, evaluation, learning, and evolution of all agents.
    """

    _instance: AgentEngine | None = None

    def __new__(cls) -> AgentEngine:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        # Core subsystems
        self._registry = AgentRegistry()
        self._router = AgentRouter()
        self._dispatcher = AgentDispatcher()
        self._events = AgentEvents()
        self._metrics = AgentMetrics()
        self._logger = AgentLogger()
        self._security = AgentSecurity()

        # Configuration
        self._orch_config = OrchestrationConfig()
        self._agent_configs: dict[str, AgentConfig] = {}
        self._team_configs: dict[str, TeamConfig] = {}

        # Runtime state
        self._running: bool = False
        self._teams: dict[str, list[str]] = {}
        self._task_history: list[dict[str, Any]] = []
        self._start_time: float | None = None

        # Subsystem references (populated during init)
        self._creation_engine = None
        self._lifecycle_engine = None
        self._communication_engine = None
        self._collaboration_engine = None
        self._memory_engine = None
        self._planning_engine = None
        self._reasoning_engine = None
        self._execution_engine = None
        self._evaluation_engine = None
        self._learning_engine = None
        self._optimizer_engine = None
        self._personality_engine = None
        self._skill_engine = None
        self._tool_manager = None
        self._marketplace_engine = None

        self._logger.info("system", "Agent Engine initialized")

    # ── Properties ──────────────────────────────────────────────

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
    def events(self) -> AgentEvents:
        return self._events

    @property
    def metrics(self) -> AgentMetrics:
        return self._metrics

    @property
    def security(self) -> AgentSecurity:
        return self._security

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def uptime(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    # ── Lifecycle ───────────────────────────────────────────────

    def start(self) -> None:
        """Start the orchestration engine."""
        if self._running:
            return
        self._running = True
        self._start_time = time.time()
        self._events.emit("engine_started", {"timestamp": time.time()})
        self._logger.info("system", "Agent Engine started")
        self._metrics.increment("engine_starts")

    def stop(self) -> None:
        """Stop the orchestration engine gracefully."""
        if not self._running:
            return
        self._running = False
        self._events.emit("engine_stopped", {"timestamp": time.time()})
        self._logger.info("system", "Agent Engine stopped")
        self._metrics.increment("engine_stops")

    def shutdown(self) -> None:
        """Full shutdown: stop engine, clear state."""
        self.stop()
        self._agent_configs.clear()
        self._team_configs.clear()
        self._teams.clear()
        self._task_history.clear()
        self._logger.info("system", "Agent Engine fully shutdown")

    # ── Agent Creation ──────────────────────────────────────────

    def create_agent(self, config: AgentConfig) -> str:
        """Create and register a new agent from config."""
        agent_id = config.agent_id
        self._agent_configs[agent_id] = config

        metadata = {
            "type": config.agent_type,
            "tier": config.tier.value,
            "name": config.name,
            "model": config.model.model,
            "capabilities": [c.value for c in config.capabilities],
            "tags": config.tags,
            "version": config.version,
        }
        self._registry.register(agent_id, metadata)
        self._events.emit("agent_created", {"agent_id": agent_id, "type": config.agent_type})
        self._metrics.increment("agents_created")
        self._logger.info(agent_id, f"Agent created: {config.name} ({config.agent_type})")
        return agent_id

    def create_agent_from_dict(self, data: dict[str, Any]) -> str:
        """Create agent from dictionary config."""
        config = AgentConfig.from_dict(data)
        return self.create_agent(config)

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the registry."""
        if self._registry.unregister(agent_id):
            self._agent_configs.pop(agent_id, None)
            self._events.emit("agent_removed", {"agent_id": agent_id})
            self._metrics.increment("agents_removed")
            return True
        return False

    def get_agent_config(self, agent_id: str) -> AgentConfig | None:
        """Get config for a specific agent."""
        return self._agent_configs.get(agent_id)

    # ── Team Management ─────────────────────────────────────────

    def create_team(self, config: TeamConfig) -> str:
        """Create a new agent team."""
        self._team_configs[config.team_id] = config
        self._teams[config.team_id] = list(config.agent_ids)
        self._events.emit("team_created", {"team_id": config.team_id})
        self._metrics.increment("teams_created")
        self._logger.info("system", f"Team created: {config.name}")
        return config.team_id

    def add_to_team(self, team_id: str, agent_id: str) -> bool:
        """Add an agent to a team."""
        if team_id not in self._teams:
            return False
        if agent_id not in self._teams[team_id]:
            self._teams[team_id].append(agent_id)
            self._events.emit("agent_joined_team", {"team_id": team_id, "agent_id": agent_id})
            return True
        return False

    def remove_from_team(self, team_id: str, agent_id: str) -> bool:
        """Remove an agent from a team."""
        if team_id in self._teams and agent_id in self._teams[team_id]:
            self._teams[team_id].remove(agent_id)
            self._events.emit("agent_left_team", {"team_id": team_id, "agent_id": agent_id})
            return True
        return False

    def get_team_agents(self, team_id: str) -> list[str]:
        """Get all agents in a team."""
        return list(self._teams.get(team_id, []))

    # ── Task Routing & Dispatch ─────────────────────────────────

    def route_task(self, task: dict[str, Any]) -> str | None:
        """Route a task to the best agent."""
        return self._router.route(task, self._registry)

    def dispatch(self, agent_id: str, task: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a task to a specific agent."""
        result = self._dispatcher.dispatch(agent_id, task)
        self._task_history.append(
            {
                "agent_id": agent_id,
                "task": task,
                "result": result,
                "timestamp": time.time(),
            }
        )
        self._metrics.increment("tasks_dispatched")
        return result

    def execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Route and dispatch a task automatically."""
        agent_id = self.route_task(task)
        if agent_id is None:
            return {"status": "error", "message": "No suitable agent found for task"}
        return self.dispatch(agent_id, task)

    # ── Health & Monitoring ─────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Get comprehensive engine health status."""
        return {
            "status": "healthy" if self._running else "stopped",
            "running": self._running,
            "uptime": self.uptime,
            "agents": self._registry.agent_count,
            "teams": len(self._teams),
            "tasks_dispatched": self._dispatcher.dispatch_count,
            "task_history_size": len(self._task_history),
            "metrics": self._metrics.snapshot(),
        }

    def snapshot(self) -> dict[str, Any]:
        """Capture full engine state."""
        return {
            "running": self._running,
            "uptime": self.uptime,
            "agents": self._registry.agent_count,
            "routes": self._router.route_count,
            "teams": len(self._teams),
            "dispatches": self._dispatcher.dispatch_count,
            "task_history": len(self._task_history),
            "agent_configs": list(self._agent_configs.keys()),
            "team_configs": list(self._team_configs.keys()),
        }

    def get_task_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent task history."""
        return self._task_history[-limit:]

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get a summary of engine metrics."""
        return self._metrics.snapshot()
