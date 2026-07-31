from __future__ import annotations

import contextlib
import time
from collections.abc import Callable
from typing import Any

from .memory_state import MemoryPhase, MemoryState

LifecycleHook = Callable[[], None]


class MemoryRuntime:
    """Runtime environment with lifecycle hooks and daemon services."""

    def __init__(self, state: MemoryState | None = None):
        self._state = state or MemoryState()
        self._hooks: dict[str, list[LifecycleHook]] = {
            "on_start": [],
            "on_ready": [],
            "on_shutdown": [],
            "on_error": [],
            "on_maintenance": [],
            "before_store": [],
            "after_store": [],
            "before_retrieve": [],
            "after_retrieve": [],
        }
        self._running: bool = False
        self._started_at: float | None = None

    @property
    def state(self) -> MemoryState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def uptime(self) -> float:
        if not self._started_at:
            return 0.0
        return time.time() - self._started_at

    def register_hook(self, event: str, hook: LifecycleHook) -> None:
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(hook)

    def unregister_hook(self, event: str, hook: LifecycleHook) -> bool:
        if event in self._hooks and hook in self._hooks[event]:
            self._hooks[event].remove(hook)
            return True
        return False

    def _run_hooks(self, event: str) -> None:
        for hook in self._hooks.get(event, []):
            with contextlib.suppress(Exception):
                hook()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._started_at = time.time()
        self._state.transition_to(MemoryPhase.INITIALIZING)
        self._run_hooks("on_start")
        self._state.transition_to(MemoryPhase.READY)
        self._run_hooks("on_ready")

    def shutdown(self) -> None:
        if not self._running:
            return
        self._running = False
        self._state.transition_to(MemoryPhase.SHUTDOWN)
        self._run_hooks("on_shutdown")

    def before_store(self) -> None:
        self._run_hooks("before_store")

    def after_store(self) -> None:
        self._run_hooks("after_store")

    def before_retrieve(self) -> None:
        self._run_hooks("before_retrieve")

    def after_retrieve(self) -> None:
        self._run_hooks("after_retrieve")

    def trigger_error(self) -> None:
        self._state.transition_to(MemoryPhase.ERROR)
        self._run_hooks("on_error")

    def trigger_maintenance(self) -> None:
        self._state.record_maintenance()
        self._run_hooks("on_maintenance")

    def to_dict(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "uptime": self.uptime,
            "state": self._state.to_dict(),
            "hooks": {k: len(v) for k, v in self._hooks.items()},
        }
