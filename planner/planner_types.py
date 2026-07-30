from __future__ import annotations

from typing import Any, Literal, TypedDict

PlanStatus = Literal["draft", "active", "completed", "failed", "cancelled"]
TaskPriority = Literal["low", "medium", "high", "critical"]
ToolType = Literal[
    "parser", "filesystem", "network", "terminal", "docker",
    "kubernetes", "git", "github", "search", "browser",
    "shell", "compiler", "profiler", "benchmark",
    "security", "validator", "database", "cache", "vector", "llm",
]


class PlanDict(TypedDict, total=False):
    id: str
    goal: str
    status: PlanStatus
    tasks: list[dict[str, Any]]
    created_at: str


class TaskDict(TypedDict, total=False):
    id: str
    name: str
    status: str
    priority: TaskPriority
    dependencies: list[str]
