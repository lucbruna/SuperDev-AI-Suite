"""AIOS Execution Context — immutable-ish context carrier.

An ExecutionContext carries everything a unit of work needs: ids,
inputs, metadata and a mutable trace of what happened during the run.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    """Carrier for a single unit of work."""

    kind: str  # "task" | "agent" | "workflow" | "plugin"
    inputs: dict[str, Any] = field(default_factory=dict)
    session_id: str | None = None
    agent_id: str | None = None
    workflow_id: str | None = None
    module_id: str | None = None
    actor: str = "system"
    metadata: dict[str, Any] = field(default_factory=dict)
    context_id: str = field(default_factory=lambda: f"ctx-{uuid.uuid4().hex[:10]}")
    created_at: float = field(default_factory=time.time)
    trace: list[dict[str, Any]] = field(default_factory=list)

    def fork(self, **overrides: Any) -> "ExecutionContext":
        """Create a child context inheriting trace and ids."""
        values = {
            "kind": self.kind,
            "inputs": dict(self.inputs),
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "workflow_id": self.workflow_id,
            "module_id": self.module_id,
            "actor": self.actor,
            "metadata": dict(self.metadata),
            "trace": list(self.trace),
        }
        values.update(overrides)
        return ExecutionContext(**values)

    def record(self, event: str, **details: Any) -> "ExecutionContext":
        self.trace.append({"event": event, "at": time.time(), **details})
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "inputs": self.inputs,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "workflow_id": self.workflow_id,
            "module_id": self.module_id,
            "actor": self.actor,
            "metadata": self.metadata,
            "context_id": self.context_id,
            "created_at": self.created_at,
            "trace": self.trace,
        }

    @staticmethod
    def make(kind: str, **kwargs: Any) -> "ExecutionContext":
        return ExecutionContext(kind=kind, **kwargs)
