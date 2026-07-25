from __future__ import annotations

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    success: bool = True
    output: str = ""
    error: str = ""
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        self._agent_id: str = str(uuid.uuid4())
        self._config: dict[str, Any] = config or {}
        self._status: str = "idle"
        self._paused: asyncio.Event = asyncio.Event()
        self._paused.set()
        self._cancelled: bool = False
        self._started_at: Optional[float] = None
        self._error_count: int = 0
        self._last_heartbeat: Optional[float] = None

    @abstractmethod
    async def initialize(self) -> None:
        ...

    @abstractmethod
    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        ...

    async def shutdown(self) -> None:
        self._status = "shutdown"

    async def pause(self) -> None:
        self._status = "paused"
        self._paused.clear()

    async def resume(self) -> None:
        self._status = "running"
        self._paused.set()

    async def cancel(self) -> None:
        self._cancelled = True
        self._status = "cancelled"
        self._paused.set()

    def status(self) -> str:
        return self._status

    def health(self) -> dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "status": self._status,
            "last_heartbeat": self._last_heartbeat,
            "error_count": self._error_count,
            "uptime": time.time() - self._started_at if self._started_at else 0,
        }

    def capabilities(self) -> list[str]:
        return []

    async def _check_cancelled(self) -> None:
        if self._cancelled:
            raise asyncio.CancelledError("Agent execution was cancelled")
        await self._paused.wait()
        if self._cancelled:
            raise asyncio.CancelledError("Agent execution was cancelled")
