from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AgentStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class AgentType(StrEnum):
    REACT = "react"
    PLANNER_EXECUTOR = "planner_executor"
    CODE = "code"
    REVIEW = "review"
    CHAT = "chat"


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]
    result: Any = None
    error: str | None = None


@dataclass
class AgentStep:
    thought: str = ""
    action: str = ""
    action_input: dict[str, Any] = field(default_factory=dict)
    observation: Any = None
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class AgentResult:
    output: str
    steps: list[AgentStep] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    token_usage: dict[str, int] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


class BaseAgent(ABC):
    """Abstract base class for AI agents."""

    def __init__(
        self,
        name: str,
        description: str = "",
        agent_type: AgentType = AgentType.REACT,
        model: str | None = None,
        provider: str | None = None,
        max_steps: int = 10,
        temperature: float = 0.7,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.agent_type = agent_type
        self.model = model
        self.provider = provider
        self.max_steps = max_steps
        self.temperature = temperature
        self.config = kwargs
        self._status = AgentStatus.IDLE
        self._tools: list[dict[str, Any]] = []

    @property
    def status(self) -> AgentStatus:
        return self._status

    def register_tool(self, name: str, description: str, parameters: dict[str, Any]) -> None:
        self._tools.append(
            {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        )

    def get_tools_schema(self) -> list[dict[str, Any]]:
        return self._tools

    @abstractmethod
    async def run(
        self,
        input_text: str,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> AgentResult: ...

    @abstractmethod
    async def think(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> str: ...

    @abstractmethod
    async def act(
        self,
        action: str,
        action_input: dict[str, Any],
        **kwargs,
    ) -> Any: ...

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type.value,
            "model": self.model,
            "provider": self.provider,
            "status": self._status.value,
            "tools": self._tools,
        }
