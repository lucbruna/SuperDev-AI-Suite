from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """State for a single agent's runtime status."""

    agent_id: str
    name: str = ""
    status: str = "idle"  # idle | running | paused | error | completed
    current_task: str | None = None
    progress: float = 0.0
    logs: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def start(self, task: str) -> None:
        self.status = "running"
        self.current_task = task
        self.progress = 0.0

    def set_progress(self, value: float) -> None:
        self.progress = max(0.0, min(100.0, value))

    def log(self, line: str) -> None:
        self.logs.append(line)

    def complete(self) -> None:
        self.status = "completed"
        self.progress = 100.0

    def fail(self, error: str) -> None:
        self.status = "error"
        self.log(f"ERROR: {error}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "current_task": self.current_task,
            "progress": self.progress,
            "logs": list(self.logs),
            "meta": dict(self.meta),
        }
