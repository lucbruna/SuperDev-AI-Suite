"""Image manager."""

from __future__ import annotations

import time
from typing import Any


class ImageManager:
    def __init__(self) -> None:
        self._images: dict[str, dict[str, Any]] = {}

    def pull(self, name: str, tag: str = "latest", registry: str = "docker.io") -> dict[str, Any]:
        image = {"name": name, "tag": tag, "registry": registry, "size_mb": 150, "pulled_at": time.time()}
        key = f"{registry}/{name}:{tag}"
        self._images[key] = image
        return image

    def list_images(self) -> list[dict[str, Any]]:
        return list(self._images.values())

    def remove(self, name: str, tag: str = "latest") -> bool:
        key = f"docker.io/{name}:{tag}"
        if key in self._images:
            del self._images[key]
            return True
        return False

    def get_image(self, name: str, tag: str = "latest") -> dict[str, Any]:
        key = f"docker.io/{name}:{tag}"
        return self._images.get(key, {"error": "not_found"})

    def count(self) -> int:
        return len(self._images)
