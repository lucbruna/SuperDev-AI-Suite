"""Developer context — the object threaded through the autonomous flow.

Carries configuration, the event bus, state tracker, registry, memory,
session manager, per-run statistics and phase artifacts so every component
shares one coherent view of the current run.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.costs import CostTracker
from modules.autonomous_developer.core.events import EventBus
from modules.autonomous_developer.core.memory import DeveloperMemory
from modules.autonomous_developer.core.registry import DeveloperRegistry, default_registry
from modules.autonomous_developer.core.session import DeveloperSession, SessionManager
from modules.autonomous_developer.core.state import DeveloperStateTracker
from modules.autonomous_developer.memory.lessons import LessonStore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DeveloperContext:
    """Shared context for one autonomous developer run."""

    config: DeveloperConfig
    # Shared process-wide registry: components registered by any phase
    # (planners, generators, validators, ...) are automatically visible to
    # every context.
    registry: DeveloperRegistry = field(default_factory=default_registry)
    bus: EventBus = field(default_factory=EventBus)
    state: DeveloperStateTracker = field(default_factory=DeveloperStateTracker)
    memory: DeveloperMemory = field(default_factory=DeveloperMemory)
    lessons: LessonStore = field(default_factory=LessonStore)
    sessions: SessionManager = field(default_factory=SessionManager)
    # Phase outputs accumulate here (plan, generated files, test results...).
    artifacts: dict[str, Any] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)
    # Per-phase execution trace and LLM usage/cost accounting.
    trace: list[dict[str, Any]] = field(default_factory=list)
    usage: CostTracker = field(default_factory=CostTracker)
    cancel_requested: bool = False
    started_at: float = field(default_factory=time.time)

    def create_session(
        self, goal: str = "", meta: dict[str, Any] | None = None
    ) -> DeveloperSession:
        return self.sessions.create(
            project_root=self.config.project_root, goal=goal, meta=meta
        )

    def request_cancel(self) -> None:
        self.cancel_requested = True
        self.bus.publish("task.cancelled", {})

    @property
    def cancelled(self) -> bool:
        return self.cancel_requested

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        self.bus.publish(event_type, payload)

    def record(self, key: str, value: Any) -> None:
        self.stats[key] = value

    def record_usage(self, phase: str, prompt_tokens: int, completion_tokens: int) -> None:
        """Track one LLM call's token usage and mirror totals into stats."""
        self.usage.record(phase, prompt_tokens, completion_tokens)
        totals = self.usage.totals()
        self.stats["llm_prompt_tokens"] = totals["prompt_tokens"]
        self.stats["llm_completion_tokens"] = totals["completion_tokens"]
        self.stats["llm_cost_usd"] = totals["cost_usd"]
        self.stats["llm_calls"] = totals["calls"]

    def record_trace(
        self,
        phase: str,
        status: str,
        *,
        elapsed_seconds: float = 0.0,
        error: str = "",
    ) -> None:
        self.trace.append(
            {
                "phase": phase,
                "status": status,
                "elapsed_seconds": round(elapsed_seconds, 4),
                "error": error,
            }
        )

    def get_artifact(self, name: str, default: Any = None) -> Any:
        return self.artifacts.get(name, default)

    def set_artifact(self, name: str, value: Any) -> None:
        self.artifacts[name] = value

    def elapsed_seconds(self) -> float:
        return round(time.time() - self.started_at, 3)
