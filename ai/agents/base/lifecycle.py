from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict


class LifecycleStage(Enum):
    CREATED = auto()
    INITIALIZED = auto()
    STARTED = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()
    DESTROYED = auto()


class Lifecycle:
    """Manages agent lifecycle transitions."""

    def __init__(self) -> None:
        self._stage = LifecycleStage.CREATED

    @property
    def stage(self) -> LifecycleStage:
        return self._stage

    def transition(self, target: LifecycleStage) -> bool:
        allowed = {
            LifecycleStage.CREATED: {LifecycleStage.INITIALIZED, LifecycleStage.DESTROYED},
            LifecycleStage.INITIALIZED: {LifecycleStage.STARTED, LifecycleStage.DESTROYED},
            LifecycleStage.STARTED: {LifecycleStage.RUNNING, LifecycleStage.STOPPED},
            LifecycleStage.RUNNING: {LifecycleStage.PAUSED, LifecycleStage.STOPPED},
            LifecycleStage.PAUSED: {LifecycleStage.RUNNING, LifecycleStage.STOPPED},
            LifecycleStage.STOPPED: {LifecycleStage.DESTROYED},
            LifecycleStage.DESTROYED: set(),
        }
        if target in allowed.get(self._stage, set()):
            self._stage = target
            return True
        return False

    def is_active(self) -> bool:
        return self._stage in (LifecycleStage.RUNNING, LifecycleStage.PAUSED)

    def to_dict(self) -> Dict[str, Any]:
        return {"stage": self._stage.name, "active": self.is_active()}
