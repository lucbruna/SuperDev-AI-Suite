from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .docker_engine import DockerEngine


class ImageManager:
    """Manages Docker images — pull, push, tag, prune (in-memory)."""

    def __init__(self, engine: DockerEngine) -> None:
        self._log = logging.getLogger("superdev.devops.docker.images")
        self._engine = engine

    def pull(self, image: str) -> dict[str, Any]:
        """Pull an image from a registry (simulated)."""
        record = {
            "image": image,
            "status": "pulled",
            "pulled_at": time.time(),
        }
        self._engine.register_image(image, record)
        self._engine._persist()
        return record

    def push(self, image: str, registry: str | None = None) -> dict[str, Any]:
        """Push an image to a registry (simulated)."""
        return {
            "image": image,
            "registry": registry or "docker.io",
            "status": "pushed",
            "pushed_at": time.time(),
        }

    def tag(self, image: str, tag: str) -> bool:
        """Create a new tag for an existing image."""
        existing = self._engine.get_image(image)
        if existing is None:
            return False
        tagged = f"{image.split(':')[0]}:{tag}"
        self._engine.register_image(tagged, {"tag": tagged, "source": image})
        self._engine._persist()
        return True

    def remove(self, image: str) -> bool:
        removed = self._engine.remove_image(image)
        if removed:
            self._engine._persist()
        return removed

    def list(self) -> list[dict[str, Any]]:
        return self._engine.list_images()
