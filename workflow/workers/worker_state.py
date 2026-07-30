from __future__ import annotations

from enum import Enum


class WorkerState(Enum):
    IDLE = "idle"
    BUSY = "busy"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
