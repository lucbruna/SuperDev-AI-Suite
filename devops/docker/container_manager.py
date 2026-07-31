from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .docker_engine import DockerEngine


class ContainerManager:
    """Manages Docker containers — run, stop, inspect, logs (in-memory)."""

    def __init__(self, engine: DockerEngine) -> None:
        self._log = logging.getLogger("superdev.devops.docker.containers")
        self._engine = engine
        self._containers: dict[str, dict[str, Any]] = {}
        self._logs: dict[str, list[str]] = {}

    def run(self, image: str, name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """Run a container from an image."""
        container_id = f"ctr-{uuid.uuid4().hex[:10]}"
        record: dict[str, Any] = {
            "container_id": container_id,
            "image": image,
            "name": name or container_id,
            "status": "running",
            "created_at": time.time(),
            "ports": kwargs.get("ports", []),
        }
        record.update({k: v for k, v in kwargs.items() if k not in ("ports",)})
        self._containers[container_id] = record
        self._logs[container_id] = [f"container {container_id} started from {image}"]
        self._engine._persist()
        return dict(record)

    def stop(self, container_id: str) -> bool:
        record = self._containers.get(container_id)
        if record is None or record["status"] == "stopped":
            return False
        record["status"] = "stopped"
        self._logs.setdefault(container_id, []).append("container stopped")
        self._engine._persist()
        return True

    def start(self, container_id: str) -> bool:
        record = self._containers.get(container_id)
        if record is None:
            return False
        record["status"] = "running"
        self._logs.setdefault(container_id, []).append("container started")
        self._engine._persist()
        return True

    def remove(self, container_id: str) -> bool:
        self._logs.pop(container_id, None)
        removed = self._containers.pop(container_id, None) is not None
        if removed:
            self._engine._persist()
        return removed

    def logs(self, container_id: str, tail: int = 100) -> list[str]:
        return list(self._logs.get(container_id, []))[-tail:]

    def inspect(self, container_id: str) -> dict[str, Any]:
        record = self._containers.get(container_id)
        if record is None:
            raise KeyError(f"container not found: {container_id}")
        return dict(record)

    def list(self) -> list[dict[str, Any]]:
        return [dict(c) for c in self._containers.values()]

    # -- persistence ---------------------------------------------------------

    def snapshot_state(self) -> dict[str, Any]:
        """Collect container records and logs for JSON persistence."""
        return {"containers": self._containers, "logs": self._logs}

    def restore_state(self, data: dict[str, Any]) -> None:
        """Restore containers and logs from persisted JSON (tolerant)."""
        containers = data.get("containers")
        if isinstance(containers, dict):
            self._containers = containers
        logs = data.get("logs")
        if isinstance(logs, dict):
            self._logs = logs
