"""Agent Manager — orchestrator-level management of all AI agents.

Wraps the existing ai/manager/agent_manager.py and ai/registry/agent_registry.py
into the orchestrator's service architecture, providing lifecycle management,
capability registration, and event propagation for all 17+ AI agents.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from .exceptions import OrchestratorError
from .types import ServiceStatus, now_iso


class AgentManager:
    """Orchestrator-level agent manager.

    Manages the full lifecycle of AI agents: registration, initialization,
    execution, health monitoring, and decommissioning. Integrates with
    the existing ai/ module through lazy imports.
    """

    # All 17 agents defined in the user's architecture
    AGENT_DEFINITIONS: dict[str, dict[str, Any]] = {
        "architect":     {"name": "Arquiteto",      "description": "System and software architecture design"},
        "backend":       {"name": "Backend",         "description": "Backend development (Python, FastAPI, etc.)"},
        "frontend":      {"name": "Frontend",        "description": "Frontend development (React, Next.js, etc.)"},
        "mobile":        {"name": "Mobile",          "description": "Mobile development (Flutter, Swift, etc.)"},
        "database":      {"name": "Banco de Dados",  "description": "Database design and optimization"},
        "devops":        {"name": "DevOps",          "description": "DevOps, CI/CD, and infrastructure"},
        "security":      {"name": "Segurança",       "description": "Security analysis and vulnerability detection"},
        "qa":            {"name": "QA/Tester",       "description": "Quality assurance and test generation"},
        "documentation": {"name": "Documentação",    "description": "Technical documentation generation"},
        "performance":   {"name": "Performance",     "description": "Performance analysis and optimization"},
        "cloud":         {"name": "Cloud",           "description": "Cloud infrastructure (AWS, Azure, GCP)"},
        "kubernetes":    {"name": "Kubernetes",      "description": "K8s orchestration and Helm charts"},
        "docker":        {"name": "Docker",          "description": "Docker containerization"},
        "git":           {"name": "Git",             "description": "Git operations and version control"},
        "ux_ui":         {"name": "UX/UI",           "description": "User experience and interface design"},
        "research":      {"name": "Research",        "description": "Code research and analysis"},
        "review":        {"name": "Code Review",     "description": "Code review and quality analysis"},
    }

    def __init__(self, event_bus: Any = None) -> None:
        self._event_bus = event_bus
        self._internal_manager: Any = None
        self._initialized = False
        self._agent_instances: dict[str, dict[str, Any]] = {}
        self._execution_history: list[dict[str, Any]] = []

    async def initialize(self) -> bool:
        """Initialize the agent manager and register all 17 agents."""
        try:
            from ai.manager.agent_manager import AgentManager as InternalManager
            from ai.core.agent_configuration import AgentConfig
            from ai.registry.agent_registry import AgentRegistry

            registry = AgentRegistry()
            self._internal_manager = InternalManager(registry=registry)

            # Register all 17 agents
            for agent_id, definition in self.AGENT_DEFINITIONS.items():
                config = AgentConfig(
                    name=agent_id,
                    description=definition["description"],
                    model="gpt-4",
                    provider="openai",
                )
                internal_id = await self._internal_manager.create_agent(config)

                self._agent_instances[agent_id] = {
                    "agent_id": agent_id,
                    "name": definition["name"],
                    "description": definition["description"],
                    "internal_id": internal_id,
                    "status": "created",
                    "capabilities": [],
                    "created_at": now_iso(),
                }

            self._initialized = True
            return True

        except ImportError as e:
            raise OrchestratorError(f"Failed to initialize AgentManager: {e}")

    async def start_agent(self, agent_id: str) -> dict[str, Any]:
        """Start a specific agent."""
        agent = self._agent_instances.get(agent_id)
        if not agent:
            raise OrchestratorError(f"Agent '{agent_id}' not found")

        internal_id = agent["internal_id"]
        try:
            await self._internal_manager.start_agent(internal_id)
            agent["status"] = "running"

            if self._event_bus:
                await self._event_bus.publish(
                    "agent.started",
                    {"agent_id": agent_id, "name": agent["name"]},
                    source="agent_manager",
                )
            return {"agent_id": agent_id, "status": "running"}
        except Exception as e:
            agent["status"] = "failed"
            raise OrchestratorError(f"Failed to start agent '{agent_id}': {e}")

    async def stop_agent(self, agent_id: str) -> dict[str, Any]:
        """Stop a specific agent."""
        agent = self._agent_instances.get(agent_id)
        if not agent:
            raise OrchestratorError(f"Agent '{agent_id}' not found")

        try:
            await self._internal_manager.stop_agent(agent["internal_id"])
            agent["status"] = "stopped"
            return {"agent_id": agent_id, "status": "stopped"}
        except Exception as e:
            raise OrchestratorError(f"Failed to stop agent '{agent_id}': {e}")

    async def execute(
        self,
        agent_id: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a task using a specific agent."""
        agent = self._agent_instances.get(agent_id)
        if not agent:
            raise OrchestratorError(f"Agent '{agent_id}' not found")

        start = time.time()

        try:
            internal_id = agent["internal_id"]
            internal_agent = self._internal_manager._instances.get(internal_id)

            if not internal_agent:
                raise OrchestratorError(f"Agent '{agent_id}' internal instance not found")

            agent_result = await internal_agent.execute(task, context or {})

            elapsed_ms = round((time.time() - start) * 1000, 2)

            entry = {
                "agent_id": agent_id,
                "task": task[:100],
                "success": agent_result.success,
                "duration_ms": elapsed_ms,
                "timestamp": now_iso(),
            }
            self._execution_history.append(entry)
            if len(self._execution_history) > 1000:
                self._execution_history = self._execution_history[-500:]

            return {
                "agent_id": agent_id,
                "success": agent_result.success,
                "output": agent_result.output,
                "error": agent_result.error,
                "metrics": agent_result.metrics,
                "duration_ms": elapsed_ms,
            }
        except Exception as e:
            elapsed_ms = round((time.time() - start) * 1000, 2)
            return {
                "agent_id": agent_id,
                "success": False,
                "error": str(e),
                "duration_ms": elapsed_ms,
            }

    async def start_all(self) -> list[dict[str, Any]]:
        """Start all registered agents."""
        results = []
        for agent_id in self._agent_instances:
            try:
                result = await self.start_agent(agent_id)
                results.append(result)
            except Exception as e:
                results.append({"agent_id": agent_id, "status": "failed", "error": str(e)})
        return results

    async def stop_all(self) -> list[dict[str, Any]]:
        """Stop all agents."""
        results = []
        for agent_id in self._agent_instances:
            try:
                result = await self.stop_agent(agent_id)
                results.append(result)
            except Exception as e:
                results.append({"agent_id": agent_id, "status": "failed", "error": str(e)})
        return results

    def list_agents(self, status: str = "") -> list[dict[str, Any]]:
        """List all agents, optionally filtered by status."""
        agents = list(self._agent_instances.values())
        if status:
            agents = [a for a in agents if a["status"] == status]
        return agents

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        """Get details for a specific agent."""
        return self._agent_instances.get(agent_id)

    def get_statistics(self) -> dict[str, Any]:
        """Get agent manager statistics."""
        agents = self._agent_instances.values()
        by_status: dict[str, int] = {}
        for a in agents:
            by_status[a["status"]] = by_status.get(a["status"], 0) + 1
        total_execs = len(self._execution_history)
        success = sum(1 for e in self._execution_history if e.get("success"))
        return {
            "total_agents": len(self._agent_instances),
            "by_status": by_status,
            "total_executions": total_execs,
            "successful": success,
            "failed": total_execs - success,
            "initialized": self._initialized,
        }
