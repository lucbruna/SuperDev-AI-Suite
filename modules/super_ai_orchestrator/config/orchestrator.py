"""Top-level orchestrator configuration."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any

from modules.super_ai_orchestrator.config.base import apply_overrides


@dataclass(slots=True)
class OrchestratorConfig:
    """Behaviour of the orchestrator as a whole.

    Attributes:
        default_priority: priority assigned when the caller gives none
            (1 = lowest urgency, 10 = highest).
        audit_enabled: whether the kernel records an immutable audit trail.
        checkpoint_enabled: whether tasks may persist checkpoints for resume.
        resume_capacity: maximum number of resumable (paused) tasks kept.
        max_attempts: maximum execution attempts per task.
        log_level: log level used by the facade (informational only).
    """

    default_priority: int = 5
    audit_enabled: bool = True
    checkpoint_enabled: bool = True
    resume_capacity: int = 16
    max_attempts: int = 1
    log_level: str = "INFO"

    def resolve(self, overrides: dict[str, Any] | None = None) -> "OrchestratorConfig":
        return apply_overrides(self, overrides)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrchestratorConfig":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})
