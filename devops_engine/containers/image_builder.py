"""Container image builder (Volume 37, Fase 2)."""

from __future__ import annotations

import hashlib

from devops_engine.devops_models import Image, ImageStatus
from devops_engine.devops_protocols import new_id, now


class ImageBuilder:
    """Builds and tags container images."""

    def __init__(self) -> None:
        self._images: dict[str, Image] = {}

    def build(self, name: str, tag: str = "latest",
              dockerfile: str = "") -> Image:
        digest = hashlib.sha256(
            f"{name}:{tag}:{dockerfile}".encode()).hexdigest()[:12]
        image = Image(
            image_id=new_id("image"),
            name=name,
            tag=tag,
            digest=digest,
            status=ImageStatus.BUILT,
            size_bytes=len(dockerfile or ""),
            created_at=now(),
        )
        self._images[image.image_id] = image
        return image

    def tag(self, image: Image, new_tag: str) -> Image:
        tagged = Image(
            image_id=new_id("image"),
            name=image.name,
            tag=new_tag,
            digest=image.digest,
            status=ImageStatus.BUILT,
            size_bytes=image.size_bytes,
            created_at=now(),
        )
        self._images[tagged.image_id] = tagged
        return tagged

    def get(self, image_id: str) -> Image | None:
        return self._images.get(image_id)

    def list(self) -> list[Image]:
        return list(self._images.values())

    def count(self) -> int:
        return len(self._images)
