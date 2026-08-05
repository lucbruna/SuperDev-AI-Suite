"""Render layers (AOV-style) — accumulate separate passes for final comp."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class RenderLayer:
    name: str
    image: NDArray[np.floating]
    visible: bool = True


class RenderLayers:
    """Named pass collection, like beauty/specular/reflection layers."""

    def __init__(self) -> None:
        self._passes: dict[str, RenderLayer] = {}

    def add(self, name: str, image: NDArray[np.floating]) -> RenderLayers:
        self._passes[name] = RenderLayer(name, np.asarray(image, dtype=np.float64))
        return self

    def get(self, name: str) -> NDArray[np.floating]:
        return self._passes[name].image

    def merge(self, order: list[str] | None = None) -> NDArray[np.floating]:
        """Add visible passes together (clamped)."""
        keys = order or list(self._passes)
        acc = None
        for k in keys:
            layer = self._passes[k]
            if layer.visible:
                acc = layer.image if acc is None else acc + layer.image
        return np.clip(acc, 0.0, 1.0) if acc is not None else np.zeros((0, 0, 3))

    def names(self) -> list[str]:
        return list(self._passes)
