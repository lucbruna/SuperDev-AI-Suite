from __future__ import annotations

import uuid
from typing import Any

from agents.communication.message_bus import MessageBus


class OrchestrationHub:
    def __init__(self, message_bus: MessageBus | None = None):
        self._bus = message_bus or MessageBus()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._agent_sessions: dict[str, str] = {}

    async def create_session(self, project_id: str) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "project_id": project_id,
            "agents": {},
            "status": "created",
            "tasks": [],
            "results": {},
            "created_at": __import__("datetime").datetime.now().isoformat(),
        }
        return session_id

    async def assign_agent(self, session_id: str, agent_id: str, role: str) -> None:
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session["agents"][agent_id] = {"role": role, "status": "idle", "tasks_completed": 0}
        self._agent_sessions[agent_id] = session_id
        await self._bus.publish("orchestrator.agent_assigned", {"session_id": session_id, "agent_id": agent_id, "role": role})

    async def assign_task(self, session_id: str, agent_id: str, task: dict[str, Any]) -> None:
        session = self._sessions.get(session_id)
        if not session:
            return
        task_id = str(uuid.uuid4())[:8]
        task["task_id"] = task_id
        task["status"] = "assigned"
        session["tasks"].append(task)
        session["agents"][agent_id]["status"] = "working"
        await self._bus.publish(f"agent.{agent_id}.task", {"session_id": session_id, "task": task})

    async def receive_result(self, agent_id: str, result: dict[str, Any]) -> None:
        session_id = self._agent_sessions.get(agent_id)
        if not session_id:
            return
        session = self._sessions.get(session_id)
        if not session:
            return
        task_id = result.get("task_id", "unknown")
        session["results"][task_id] = result
        session["agents"][agent_id]["tasks_completed"] += 1
        session["agents"][agent_id]["status"] = "idle"
        completed = sum(1 for t in session["tasks"] if t["task_id"] in session["results"])
        total = len(session["tasks"])
        if completed >= total and total > 0:
            session["status"] = "completed"
            await self._bus.publish("orchestrator.session_completed", {"session_id": session_id})

    async def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    async def list_sessions(self) -> list[dict[str, Any]]:
        return [{"session_id": sid, **s} for sid, s in self._sessions.items()]

    async def broadcast(self, session_id: str, message: Any) -> None:
        session = self._sessions.get(session_id)
        if not session:
            return
        for agent_id in session["agents"]:
            await self._bus.publish(f"agent.{agent_id}.broadcast", {"session_id": session_id, "message": message})

    async def get_agent_status(self, agent_id: str) -> dict[str, Any] | None:
        session_id = self._agent_sessions.get(agent_id)
        if not session_id:
            return None
        session = self._sessions.get(session_id)
        if not session:
            return None
        return session["agents"].get(agent_id)
