"""Container image registry (Volume 37, Fase 2)."""

from __future__ import annotations

from devops_engine.devops_models import Image, ImageStatus


class RegistryManager:
    """Pushes and pulls images by name:tag."""

    def __init__(self) -> None:
        self._images: dict[str, Image] = {}

    def push(self, image: Image) -> bool:
        self._images[f"{image.name}:{image.tag}"] = image
        image.status = ImageStatus.PUSHED
        return True

    def pull(self, name: str, tag: str = "latest") -> Image | None:
        return self._images.get(f"{name}:{tag}")

    def list(self) -> list[Image]:
        return list(self._images.values())

    def count(self) -> int:
        return len(self._images)
