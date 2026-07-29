from __future__ import annotations

from typing import Any

from ..core.agent_configuration import AgentConfig
from .engine import OrchestratorEngine
from .health import AgentHealthMonitor


class OrchestratorAPI:
    """Integration layer between the orchestrator and the FastAPI backend."""

    def __init__(self, engine: OrchestratorEngine | None = None) -> None:
        self._initialized = False
        if engine:
            self.engine = engine
            self.health = AgentHealthMonitor()
            self._initialized = True

    @classmethod
    async def create(cls) -> OrchestratorAPI:
        """Factory method that creates and initializes the orchestrator."""
        api = cls()
        engine = OrchestratorEngine()
        health = AgentHealthMonitor()

        api.engine = engine
        api.health = health
        api._initialized = True

        await engine.start()
        await health.start_monitoring()
        return api

    # === Session Management ===

    async def create_session(
        self,
        project_id: str = "",
        name: str = "",
        strategy: str = "pipeline",
    ) -> dict[str, Any]:
        return await self.engine.create_orchestration(
            project_id=project_id, name=name, strategy=strategy,
        )

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        session = await self.engine.state.get_session(session_id)
        if not session:
            return None
        return session.model_dump(mode="json")

    async def list_sessions(
        self, status: str | None = None, limit: int = 50, offset: int = 0,
    ) -> list[dict[str, Any]]:
        sessions = await self.engine.state.list_sessions(
            status=status, limit=limit, offset=offset,
        )
        return [s.model_dump(mode="json") for s in sessions]

    async def delete_session(self, session_id: str) -> bool:
        return await self.engine.state.delete_session(session_id)

    # === Pipeline Execution ===

    async def run_pipeline(
        self,
        session_id: str,
        strategy: str = "pipeline",
        tasks: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return await self.engine.run_pipeline(
            session_id=session_id, tasks=tasks, strategy=strategy,
        )

    async def run_with_prompt(
        self,
        prompt: str,
        project_id: str = "",
        strategy: str = "pipeline",
    ) -> dict[str, Any]:
        return await self.engine.orchestrate_with_prompt(
            prompt=prompt, project_id=project_id, strategy=strategy,
        )

    # === Agent Management ===

    async def list_agents(self) -> list[dict[str, Any]]:
        return await self.engine.get_agents_status()

    async def get_agent(self, agent_id: str) -> dict[str, Any]:
        status = self.engine.agent_manager.get_agent_status(agent_id)
        if status.get("status") == "not_found":
            return {"error": "Agent not found"}
        return {
            **status,
            "health_report": self.health.get_report(agent_id).__dict__
            if self.health.get_report(agent_id) else {},
            "load": self.engine.router.get_agent_load(agent_id),
        }

    async def create_agent(
        self, name: str, description: str = "",
        model: str = "gpt-4", provider: str = "openai",
    ) -> dict[str, Any]:
        config = AgentConfig(
            name=name, description=description,
            model=model, provider=provider,
        )
        agent_id = await self.engine.agent_manager.create_agent(config)
        self.health.register_agent(agent_id, name)
        return {"agent_id": agent_id, "name": name, "status": "created"}

    async def start_agent(self, agent_id: str) -> bool:
        try:
            await self.engine.agent_manager.start_agent(agent_id)
            self.health.record_heartbeat(agent_id, "running")
            return True
        except ValueError:
            return False

    async def stop_agent(self, agent_id: str) -> bool:
        try:
            await self.engine.agent_manager.stop_agent(agent_id)
            self.health.record_heartbeat(agent_id, "paused")
            return True
        except ValueError:
            return False

    async def delete_agent(self, agent_id: str) -> bool:
        try:
            await self.engine.agent_manager.destroy_agent(agent_id)
            self.health.unregister_agent(agent_id)
            return True
        except ValueError:
            return False

    # === Health & Metrics ===

    async def get_health_summary(self) -> dict[str, Any]:
        return self.health.get_summary()

    async def get_health_reports(self) -> list[dict[str, Any]]:
        return self.health.get_all_reports()

    async def get_metrics(self) -> dict[str, Any]:
        return self.engine.get_metrics()

    async def get_routing_stats(self) -> dict[str, Any]:
        return self.engine.router.get_statistics()

    async def get_route_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.engine.router.get_route_history(limit=limit)

    # === Shutdown ===

    async def shutdown(self) -> None:
        await self.engine.stop()
        await self.health.stop_monitoring()
