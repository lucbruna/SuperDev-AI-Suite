"""AIOS Kernel Events — typed event model and event name constants.

Kernel-level events are plain data. Delivery is handled by the
communications ``EventBus``; this module only defines the contract
and helpers so the rest of the platform stays decoupled from the bus.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

# Canonical event name constants (namespace "aios.<domain>.<event>").
KERNEL_BOOTED = "aios.kernel.booted"
KERNEL_SHUTDOWN = "aios.kernel.shutdown"
AGENT_STARTED = "aios.agent.started"
AGENT_FINISHED = "aios.agent.finished"
WORKFLOW_STARTED = "aios.workflow.started"
WORKFLOW_FINISHED = "aios.workflow.finished"
MODULE_REGISTERED = "aios.module.registered"
MODULE_UNREGISTERED = "aios.module.unregistered"
MEMORY_STORED = "aios.memory.stored"
MEMORY_RECALLED = "aios.memory.recalled"
POLICY_VIOLATION = "aios.governance.policy_violation"
HEALTH_DEGRADED = "aios.health.degraded"
FAILURE_DETECTED = "aios.self_healing.failure_detected"
RECOVERY_COMPLETED = "aios.self_healing.recovery_completed"

ALL_EVENTS: tuple[str, ...] = (
    KERNEL_BOOTED,
    KERNEL_SHUTDOWN,
    AGENT_STARTED,
    AGENT_FINISHED,
    WORKFLOW_STARTED,
    WORKFLOW_FINISHED,
    MODULE_REGISTERED,
    MODULE_UNREGISTERED,
    MEMORY_STORED,
    MEMORY_RECALLED,
    POLICY_VIOLATION,
    HEALTH_DEGRADED,
    FAILURE_DETECTED,
    RECOVERY_COMPLETED,
)


@dataclass(slots=True)
class KernelEvent:
    """A single platform event."""

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "aios"
    event_id: str = field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:10]}")
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "type": self.type,
            "source": self.source,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


def make_event(
    event_type: str,
    payload: dict[str, Any] | None = None,
    source: str = "aios",
) -> KernelEvent:
    return KernelEvent(type=event_type, payload=payload or {}, source=source)
