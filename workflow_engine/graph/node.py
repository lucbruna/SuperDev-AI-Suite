from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(StrEnum):
    AGENT = "AGENT"
    TOOL = "TOOL"
    CONDITION = "CONDITION"
    LOOP = "LOOP"
    PARALLEL = "PARALLEL"
    APPROVAL = "APPROVAL"
    WAIT = "WAIT"
    TIMER = "TIMER"
    WEBHOOK = "WEBHOOK"
    HTTP = "HTTP"
    PYTHON = "PYTHON"
    SHELL = "SHELL"
    DOCKER = "DOCKER"
    DATABASE = "DATABASE"
    HUMAN = "HUMAN"


class NodeHandle(BaseModel):
    id: str
    label: str
    type: str = "default"


class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    name: str
    config: dict[str, Any] = Field(default_factory=dict)
    position: tuple[float, float] = (0.0, 0.0)
    description: str = ""
    inputs: list[NodeHandle] = Field(default_factory=list)
    outputs: list[NodeHandle] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
