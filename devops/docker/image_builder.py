from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .docker_engine import DockerEngine


class ImageBuilder:
    """Builds Docker images from Dockerfiles or build contexts (in-memory)."""

    def __init__(self, engine: DockerEngine) -> None:
        self._log = logging.getLogger("superdev.devops.docker.image_builder")
        self._engine = engine
        self._builds: dict[str, dict[str, Any]] = {}

    def build(self, path: str, tag: str, **kwargs: Any) -> dict[str, Any]:
        """Build an image from a build context path."""
        build_id = f"build-{uuid.uuid4().hex[:8]}"
        record: dict[str, Any] = {
            "build_id": build_id,
            "path": path,
            "tag": tag,
            "status": "completed",
            "image": tag,
            "created_at": time.time(),
            "steps": [{"name": "context", "status": "ok"}, {"name": "layer", "status": "ok"}],
        }
        record.update(kwargs)
        self._builds[build_id] = record
        self._engine.register_image(tag, {"tag": tag, "build_id": build_id})
        self._log.info("docker build %s (%s) completed", build_id, tag)
        self._engine._persist()
        return dict(record)

    def build_from_dockerfile(self, dockerfile: str, tag: str, context: str = ".") -> dict[str, Any]:
        """Build an image from inline Dockerfile content."""
        build_id = f"build-{uuid.uuid4().hex[:8]}"
        record = {
            "build_id": build_id,
            "path": context,
            "dockerfile": dockerfile,
            "tag": tag,
            "status": "completed",
            "image": tag,
            "created_at": time.time(),
        }
        self._builds[build_id] = record
        self._engine.register_image(tag, {"tag": tag, "build_id": build_id})
        self._engine._persist()
        return dict(record)

    def cancel(self, build_id: str) -> bool:
        """Cancel an in-flight build (only works on non-terminal builds)."""
        record = self._builds.get(build_id)
        if record is None or record["status"] in ("completed", "failed", "cancelled"):
            return False
        record["status"] = "cancelled"
        return True

    def get(self, build_id: str) -> dict[str, Any]:
        return dict(self._builds[build_id])

    def list(self) -> list[dict[str, Any]]:
        return [dict(b) for b in self._builds.values()]

    # -- persistence ---------------------------------------------------------

    def snapshot_state(self) -> dict[str, Any]:
        """Collect the build records for JSON persistence."""
        return {"builds": self._builds}

    def restore_state(self, data: dict[str, Any]) -> None:
        """Restore build records from persisted JSON (tolerant of bad shapes)."""
        builds = data.get("builds")
        if isinstance(builds, dict):
            self._builds = builds
