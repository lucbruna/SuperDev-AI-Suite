from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..devops_store import load_json, save_json
from .container_manager import ContainerManager
from .image_builder import ImageBuilder
from .image_manager import ImageManager


class DockerEngine:
    """Central engine for Docker container management (in-memory)."""

    def __init__(self, store_path: str | Path | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.docker")
        self._store = Path(store_path) if store_path else None
        self.images = ImageManager(self)
        self.containers = ContainerManager(self)
        self.builder = ImageBuilder(self)
        self._image_store: dict[str, dict[str, Any]] = {}
        self._load_state()

    def build(self, path: str, tag: str, **kwargs: Any) -> dict[str, Any]:
        """Build a Docker image from a context path."""
        return self.builder.build(path, tag, **kwargs)

    def run(self, image: str, **kwargs: Any) -> dict[str, Any]:
        """Run a container from an image."""
        return self.containers.run(image, **kwargs)

    def stop(self, container_id: str) -> bool:
        return self.containers.stop(container_id)

    def inspect(self, container_id: str) -> dict[str, Any]:
        """Inspect a running/stopped container."""
        return self.containers.inspect(container_id)

    def list_containers(self) -> list[dict[str, Any]]:
        return self.containers.list()

    def list_images(self) -> list[dict[str, Any]]:
        return [dict(i) for i in self._image_store.values()]

    # -- image store (used by ImageBuilder/ImageManager) ----------------------

    def register_image(self, name: str, image: dict[str, Any]) -> None:
        self._image_store[name] = image

    def get_image(self, name: str) -> dict[str, Any] | None:
        return self._image_store.get(name)

    def remove_image(self, name: str) -> bool:
        return self._image_store.pop(name, None) is not None

    # -- status ---------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "images": len(self._image_store),
            "containers": len(self.containers.list()),
            "builds": len(self.builder.list()),
        }

    # -- persistence ----------------------------------------------------------

    def _load_state(self) -> None:
        """Restore images, builds and containers from the JSON store."""
        if self._store is None:
            return
        data = load_json(self._store / "docker.json", default={})
        if not isinstance(data, dict):
            return
        images = data.get("images")
        if isinstance(images, dict):
            self._image_store = images
        builds = data.get("builds")
        if isinstance(builds, dict):
            self.builder.restore_state(builds)
        containers = data.get("containers")
        if isinstance(containers, dict):
            self.containers.restore_state(containers)

    def _persist(self) -> None:
        """Atomically write the full docker state to ``docker.json``."""
        if self._store is None:
            return
        save_json(
            self._store / "docker.json",
            {
                "images": self._image_store,
                "builds": self.builder.snapshot_state(),
                "containers": self.containers.snapshot_state(),
            },
        )

    def save_state(self) -> None:
        """Persist docker state to disk (no-op without ``store_path``)."""
        self._persist()

    def reload_state(self) -> None:
        """Reload docker state from disk."""
        self._load_state()
