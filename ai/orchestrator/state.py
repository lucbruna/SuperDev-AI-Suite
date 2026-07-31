from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentAssignment(BaseModel):
    agent_id: str
    agent_name: str
    role: str
    status: str = "idle"
    tasks_completed: int = 0
    assigned_at: str = ""


class TaskState(BaseModel):
    task_id: str
    description: str
    agent_id: str = ""
    agent_name: str = ""
    status: str = "pending"
    task_type: str = ""
    depends_on: list[str] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)
    error: str = ""
    started_at: str = ""
    completed_at: str = ""
    retry_count: int = 0
    max_retries: int = 3


class SessionState(BaseModel):
    session_id: str
    project_id: str = ""
    name: str = ""
    status: str = "created"
    strategy: str = "pipeline"
    agents: dict[str, AgentAssignment] = Field(default_factory=dict)
    tasks: list[TaskState] = Field(default_factory=list)
    results: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""
    error: str = ""


class OrchestrationState:
    """Manages orchestration session state with optional file persistence."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._persist_path: str | None = None

    def configure_persistence(self, path: str) -> None:
        self._persist_path = path

    async def create_session(
        self,
        project_id: str = "",
        name: str = "",
        strategy: str = "pipeline",
    ) -> SessionState:
        now = datetime.now(UTC).isoformat()
        session = SessionState(
            session_id=str(uuid.uuid4()),
            project_id=project_id,
            name=name or f"Session-{uuid.uuid4().hex[:6]}",
            status="created",
            strategy=strategy,
            created_at=now,
            updated_at=now,
        )
        self._sessions[session.session_id] = session
        await self._persist()
        return session

    async def get_session(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    async def update_session(self, session_id: str, **updates: Any) -> SessionState | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.updated_at = datetime.now(UTC).isoformat()
        await self._persist()
        return session

    async def add_task(
        self,
        session_id: str,
        description: str,
        agent_id: str = "",
        agent_name: str = "",
        task_type: str = "",
        depends_on: list[str] | None = None,
        max_retries: int = 3,
    ) -> TaskState | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        task = TaskState(
            task_id=uuid.uuid4().hex[:8],
            description=description,
            agent_id=agent_id,
            agent_name=agent_name,
            task_type=task_type,
            depends_on=depends_on or [],
            max_retries=max_retries,
        )
        session.tasks.append(task)
        session.updated_at = datetime.now(UTC).isoformat()
        await self._persist()
        return task

    async def update_task(self, session_id: str, task_id: str, **updates: Any) -> TaskState | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        for task in session.tasks:
            if task.task_id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                if updates.get("status") == "running" and not task.started_at:
                    task.started_at = datetime.now(UTC).isoformat()
                if updates.get("status") in ("completed", "failed", "cancelled"):
                    task.completed_at = datetime.now(UTC).isoformat()
                session.updated_at = datetime.now(UTC).isoformat()
                await self._persist()
                return task
        return None

    async def assign_agent(
        self,
        session_id: str,
        agent_id: str,
        agent_name: str,
        role: str = "assistant",
    ) -> AgentAssignment | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        assignment = AgentAssignment(
            agent_id=agent_id,
            agent_name=agent_name,
            role=role,
            assigned_at=datetime.now(UTC).isoformat(),
        )
        session.agents[agent_id] = assignment
        session.updated_at = datetime.now(UTC).isoformat()
        await self._persist()
        return assignment

    async def complete_session(self, session_id: str) -> SessionState | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.status = "completed"
        session.completed_at = datetime.now(UTC).isoformat()
        session.updated_at = session.completed_at
        await self._persist()
        return session

    async def fail_session(self, session_id: str, error: str = "") -> SessionState | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.status = "failed"
        session.error = error
        session.completed_at = datetime.now(UTC).isoformat()
        session.updated_at = session.completed_at
        await self._persist()
        return session

    async def list_sessions(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SessionState]:
        sessions = list(self._sessions.values())
        if status:
            sessions = [s for s in sessions if s.status == status]
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions[offset : offset + limit]

    async def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            await self._persist()
            return True
        return False

    async def _persist(self) -> None:
        if not self._persist_path:
            return
        try:
            data = {
                sid: session.model_dump(mode="json")
                for sid, session in self._sessions.items()
            }
            with open(self._persist_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass

    async def load_from_file(self, path: str) -> int:
        count = 0
        try:
            with open(path) as f:
                data = json.load(f)
            for sid, session_data in data.items():
                self._sessions[sid] = SessionState(**session_data)
                count += 1
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return count

    def get_statistics(self) -> dict[str, Any]:
        total = len(self._sessions)
        by_status: dict[str, int] = {}
        total_tasks = 0
        completed_tasks = 0
        failed_tasks = 0

        for session in self._sessions.values():
            by_status[session.status] = by_status.get(session.status, 0) + 1
            total_tasks += len(session.tasks)
            for task in session.tasks:
                if task.status == "completed":
                    completed_tasks += 1
                elif task.status == "failed":
                    failed_tasks += 1

        return {
            "total_sessions": total,
            "by_status": by_status,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": round(completed_tasks / total_tasks, 3) if total_tasks > 0 else 0,
        }
