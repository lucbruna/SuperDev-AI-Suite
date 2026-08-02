"""Runtime context — immutable-ish execution context for a session."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeContext:
    """Everything a runtime session needs to know about its execution."""

    name: str
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    timeout_s: float | None = None
    sandbox_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "cwd": self.cwd,
            "timeout_s": self.timeout_s,
            "sandbox_id": self.sandbox_id,
            "env_keys": sorted(self.env),
            "input_keys": sorted(self.inputs),
            "metadata": dict(self.metadata),
        }


def context(name: str, **kwargs: Any) -> RuntimeContext:
    return RuntimeContext(name=name, **kwargs)


__all__ = ["RuntimeContext", "context"]
