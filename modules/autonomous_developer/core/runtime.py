"""Developer runtime — wires configuration and shared components together.

Owns the resolved config, the context (bus, state, registry, memory,
sessions, artifacts) and the phase orchestration used by managers, agents and
the API. Phases dispatch to registered components:

- ``plan``      → ``planner`` component  (kind "planner")
- ``implement`` → ``generator`` component (kind "generator")
- ``test``      → ``validator`` component (kind "validator")
- ``review``    → ``reviewer`` component  (kind "reviewer")

Components expose ``run(ctx, **kwargs) -> Any`` and their results land in
``ctx.artifacts[phase]``.
"""
from __future__ import annotations

import logging
import time
from typing import Any

from modules.autonomous_developer.config import DeveloperConfig, get_default_config
from modules.autonomous_developer.config.constants import (
    PHASE_IMPLEMENT,
    PHASE_MERGE,
    PHASE_PLAN,
    PHASE_REVIEW,
    PHASE_TEST,
)
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.core.state import DeveloperState

logger = logging.getLogger(__name__)

_PHASE_ORDER: tuple[str, ...] = (
    PHASE_PLAN,
    PHASE_IMPLEMENT,
    PHASE_TEST,
    PHASE_REVIEW,
    PHASE_MERGE,
)

_PHASE_STATES: dict[str, DeveloperState] = {
    PHASE_PLAN: DeveloperState.PLANNING,
    PHASE_IMPLEMENT: DeveloperState.IMPLEMENTING,
    PHASE_TEST: DeveloperState.TESTING,
    PHASE_REVIEW: DeveloperState.REVIEWING,
    PHASE_MERGE: DeveloperState.MERGING,
}

_PHASE_KINDS: dict[str, str] = {
    PHASE_PLAN: "planner",
    PHASE_IMPLEMENT: "generator",
    PHASE_TEST: "validator",
    PHASE_REVIEW: "reviewer",
    PHASE_MERGE: "executor",
}


class DeveloperRuntime:
    """Bundle of config + context + phase orchestration."""

    def __init__(
        self,
        config: DeveloperConfig | None = None,
        *,
        registry: Any = None,
    ) -> None:
        self.config = config or get_default_config()
        self.config.resolve()
        if registry is not None:
            self.context = DeveloperContext(config=self.config, registry=registry)
        else:
            self.context = DeveloperContext(config=self.config)
        self._lesson_learner = LessonLearner()
        self.context.bus.subscribe("task.failed", self._on_task_failed)

    def _on_task_failed(self, event) -> None:
        self._lesson_learner.on_task_failed(event.payload, self.context)

    # Convenience accessors -------------------------------------------------
    @property
    def bus(self):
        return self.context.bus

    @property
    def state(self):
        return self.context.state

    @property
    def registry(self):
        return self.context.registry

    @property
    def memory(self):
        return self.context.memory

    @property
    def sessions(self):
        return self.context.sessions

    # ── Phase orchestration ───────────────────────────────────────────────
    def run_phase(self, phase: str, **kwargs: Any) -> Any:
        """Run one phase by dispatching to its registered component.

        The component result is stored in ``ctx.artifacts[phase]`` and the
        phase state + events are recorded around the call.
        """
        if phase not in _PHASE_KINDS:
            raise DeveloperError(f"Unknown phase: {phase}", context={"phase": phase})
        kind = _PHASE_KINDS[phase]
        component = self.registry.get(kind, "default")
        self.state.set_state(_PHASE_STATES[phase], context=phase)
        self.bus.publish("phase.started", {"phase": phase})
        started = time.time()
        try:
            result = component.run(self.context, **kwargs)
        except Exception as exc:  # noqa: BLE001 — record failure, re-raise
            self.context.record_trace(
                phase, "failed", elapsed_seconds=time.time() - started, error=str(exc)
            )
            raise
        self.context.set_artifact(phase, result)
        self.context.record(f"{phase}_completed", 1)
        self.context.record_trace(
            phase, "completed", elapsed_seconds=time.time() - started
        )
        self.bus.publish("phase.completed", {"phase": phase})
        return result

    def execute(
        self,
        goal: str,
        *,
        meta: dict[str, Any] | None = None,
        phases: tuple[str, ...] | list[str] | None = None,
    ) -> DeveloperContext:
        """Run the autonomous flow for ``goal`` and return the context.

        Creates a session, runs each phase in order through its registered
        component, publishes lifecycle events and closes the session.
        """
        session = self.context.create_session(goal=goal, meta=meta)
        self.context.record("goal", goal)
        self.context.record("session_id", session.session_id)
        self.bus.publish("task.started", {"goal": goal, "session_id": session.session_id})

        phase_list = tuple(phases) if phases is not None else _PHASE_ORDER
        error: str | None = None
        failed_phase: str | None = None
        for phase in phase_list:
            if self.context.cancelled:
                break
            try:
                self.run_phase(phase, goal=goal, session_id=session.session_id)
            except Exception as exc:  # noqa: BLE001 — orchestrator must not die
                error = str(exc)
                failed_phase = phase
                self.state.mark_error(error, context={"phase": phase, "goal": goal})
                break

        if error is not None:
            self.context.sessions.complete(session, success=False)
            self.bus.publish(
                "task.failed",
                {
                    "phase": failed_phase,
                    "error": error,
                    "goal": goal,
                    "session_id": session.session_id,
                },
            )
        elif self.context.cancelled:
            self.state.set_state(DeveloperState.READY, context="cancelled")
            self.context.sessions.cancel(session)
            self.bus.publish(
                "task.cancelled", {"goal": goal, "session_id": session.session_id}
            )
        else:
            self.state.set_state(DeveloperState.READY, context="execute")
            self.context.sessions.complete(session, success=True)
            self.bus.publish(
                "task.completed", {"goal": goal, "session_id": session.session_id}
            )
        return self.context

    def status(self) -> dict[str, Any]:
        """Current runtime status for dashboards and the API."""
        return {
            "state": self.context.state.to_dict(),
            "stats": dict(self.context.stats),
            "registry": self.context.registry.counts(),
            "memory": self.context.memory.stats(),
            "lessons": self.context.lessons.stats(),
            "sessions_active": len(self.context.sessions.active()),
            "artifacts": list(self.context.artifacts),
            "trace": list(self.context.trace),
            "cost": self.context.usage.totals(),
            "config": {
                "name": self.config.name,
                "version": self.config.version,
                "mode": self.config.mode,
                "work_branch": self.config.work_branch,
                "allow_main_branch_writes": self.config.allow_main_branch_writes,
                "project_root": self.config.project_root,
                "data_dir": self.config.data_dir,
            },
        }

    def reset(self, *, keep_config: bool = True) -> None:
        """Reset state, memory, lessons, artifacts and sessions (config kept)."""
        self.context.state.reset()
        self.context.memory.clear()
        self.context.lessons.clear()
        self.context.sessions.close_all()
        self.context.artifacts.clear()
        self.context.stats.clear()
        self.context.trace.clear()
        self.context.usage.reset()
        self.context.cancel_requested = False
        if not keep_config:
            self.config = get_default_config()
            self.config.resolve()
            self.context = DeveloperContext(config=self.config)
        logger.info("Developer runtime reset")

    @classmethod
    def from_config(cls, config: DeveloperConfig | None = None) -> DeveloperRuntime:
        """Factory kept for callers that prefer a classmethod style."""
        return cls(config)


def build_runtime(config: DeveloperConfig | None = None) -> DeveloperRuntime:
    """Build a runtime from an optional config (defaults to resolved config)."""
    return DeveloperRuntime(config)


# Load phase components and register their defaults with the shared default
# registry so execute() runs the real flow. Kept at the bottom: the phase
# packages are core-free, and by this point the registry module is already
# initialized. Later phases add validator/reviewer/executor defaults here.
from modules.autonomous_developer.core.registry import default_registry  # noqa: E402
from modules.autonomous_developer.execution.merge import GitPrExecutor  # noqa: E402,F401
from modules.autonomous_developer.generator import CodeGenerator  # noqa: E402,F401
from modules.autonomous_developer.memory.lessons import LessonLearner  # noqa: E402,F401
from modules.autonomous_developer.planner import LLMPlanner  # noqa: E402,F401
from modules.autonomous_developer.review import CodeReviewer  # noqa: E402,F401
from modules.autonomous_developer.validation.test_runner import (  # noqa: E402,F401
    TestRunnerValidator,
)

default_registry().register("planner", "default", LLMPlanner())
default_registry().register("generator", "default", CodeGenerator())
default_registry().register("validator", "default", TestRunnerValidator())
default_registry().register("reviewer", "default", CodeReviewer())
default_registry().register("executor", "default", GitPrExecutor())
