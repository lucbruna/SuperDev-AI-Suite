import uuid
import logging
from datetime import datetime
from typing import Any

from runtime_engine.core.configuration import RuntimeConfig
from runtime_engine.core.runtime_kernel import RuntimeKernel
from runtime_engine.runtime.runtime_session import RuntimeSession, SessionStatus

logger = logging.getLogger(__name__)


class RuntimeManager:
    def __init__(self, kernel: RuntimeKernel) -> None:
        self._kernel = kernel

    async def create_session(self, config: dict[str, Any] | None = None) -> str:
        session_id = str(uuid.uuid4())
        merged = self._kernel.config.model_dump()
        if config:
            merged.update(config)
        session_config = RuntimeConfig(**merged)
        session = RuntimeSession(
            id=session_id,
            language=config.get("language", "python") if config else "python",
            config=session_config,
        )
        session.status = SessionStatus.RUNNING
        self._kernel.session_manager.add(session)
        await self._kernel.logs.log("INFO", f"Session {session_id} created", session_id)
        return session_id

    async def get_session(self, session_id: str) -> RuntimeSession | None:
        return self._kernel.session_manager.get(session_id)

    async def destroy_session(self, session_id: str) -> bool:
        session = self._kernel.session_manager.get(session_id)
        if session is None:
            return False
        await self._kernel.sandbox_manager.destroy_sandbox(session_id)
        session.status = SessionStatus.CANCELLED
        self._kernel.session_manager.remove(session_id)
        await self._kernel.logs.log("INFO", f"Session {session_id} destroyed", session_id)
        return True

    async def list_sessions(self) -> list[RuntimeSession]:
        return self._kernel.session_manager.list_all()

    async def get_stats(self) -> dict[str, Any]:
        sessions = await self.list_sessions()
        active = sum(1 for s in sessions if s.status == SessionStatus.RUNNING)
        return {
            "total_sessions": len(sessions),
            "active_sessions": active,
            "completed_sessions": sum(1 for s in sessions if s.status == SessionStatus.COMPLETED),
            "failed_sessions": sum(1 for s in sessions if s.status == SessionStatus.FAILED),
        }
