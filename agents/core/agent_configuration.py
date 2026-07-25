from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    agent_id: str = ""
    name: str = ""
    description: str = ""
    model: str = "gpt-4"
    provider: str = "openai"
    max_iterations: int = 10
    timeout: int = 300
    tools: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    memory_config: dict[str, Any] = Field(default_factory=dict)
