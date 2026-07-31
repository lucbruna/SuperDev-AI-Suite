"""Runtime lifecycle for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_logger import get_logger


class CollaborationRuntime:
    """Start/stop lifecycle with idempotent transitions."""

    def __init__(self, name: str = "collaboration") -> None:
        self._log = get_logger()
        self.name = name
        self.running = False

    def start(self) -> bool:
        if self.running:
            return False
        self.running = True
        self._log.info("%s runtime started", self.name)
        return True

    def stop(self) -> bool:
        if not self.running:
            return False
        self.running = False
        self._log.info("%s runtime stopped", self.name)
        return True

    def state(self) -> dict[str, Any]:
        return {"name": self.name, "running": self.running}
