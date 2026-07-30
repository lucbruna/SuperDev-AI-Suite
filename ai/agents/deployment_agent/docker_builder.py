from __future__ import annotations

from typing import Any


class DockerBuilder:
    """Builds Dockerfile configurations."""

    def __init__(self) -> None:
        self._base_image: str = "python:3.11-slim"
        self._layers: list[str] = []

    def set_base(self, image: str) -> str:
        self._base_image = image
        return image

    def add_layer(self, instruction: str) -> str:
        self._layers.append(instruction)
        return instruction

    @property
    def layers(self) -> list[str]:
        return self._layers

    @property
    def layer_count(self) -> int:
        return len(self._layers)

    def build(self) -> str:
        lines: list[str] = [f"FROM {self._base_image}"]
        lines.extend(self._layers)
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_image": self._base_image,
            "layers": self._layers,
            "layer_count": self.layer_count,
        }
