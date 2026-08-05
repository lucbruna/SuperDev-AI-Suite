"""Layer manager — flat (non-node) stack compositing for simple pipelines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .blending_modes import blend


@dataclass
class Layer:
    id: str
    image: NDArray[np.floating]
    mode: str = "normal"
    opacity: float = 1.0
    visible: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


class LayerManager:
    """Stack of layers composited bottom-to-top."""

    def __init__(self, size: tuple[int, int] | None = None) -> None:
        self._layers: list[Layer] = []
        self._size = size

    def add(self, layer: Layer) -> LayerManager:
        self._layers.append(layer)
        if self._size is None:
            self._size = (layer.image.shape[0], layer.image.shape[1])
        return self

    def remove(self, layer_id: str) -> bool:
        before = len(self._layers)
        self._layers = [l for l in self._layers if l.id != layer_id]
        return len(self._layers) != before

    def reorder(self, layer_id: str, new_index: int) -> None:
        layer = next((l for l in self._layers if l.id == layer_id), None)
        if layer is None:
            raise KeyError(layer_id)
        self._layers.remove(layer)
        new_index = max(0, min(new_index, len(self._layers)))
        self._layers.insert(new_index, layer)

    def composite(self) -> NDArray[np.floating]:
        if not self._layers:
            raise ValueError("no layers to composite")
        h, w = self._size or self._layers[-1].image.shape[:2]
        canvas = np.zeros((h, w, 3), dtype=np.float64)
        for layer in self._layers:
            if not layer.visible:
                continue
            img = layer.image
            if img.shape[:2] != (h, w):
                img = np.resize(img, (h, w, 3))
            canvas = blend(canvas, img, mode=layer.mode, amount=layer.opacity)
        return np.clip(canvas, 0.0, 1.0)

    def __len__(self) -> int:
        return len(self._layers)
