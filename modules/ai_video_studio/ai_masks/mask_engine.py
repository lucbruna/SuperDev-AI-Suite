"""Mask engine — manages named masks and applies them to frames."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass
class Mask:
    id: str
    data: NDArray[np.floating]  # float 0..1, shape (H, W) or (H, W, 1)
    meta: dict[str, Any] = field(default_factory=dict)

    def as_2d(self) -> NDArray[np.floating]:
        return self.data[..., 0] if self.data.ndim == 3 else self.data

    @classmethod
    def circle(
        cls,
        height: int,
        width: int,
        radius: float,
        cx: float | None = None,
        cy: float | None = None,
        *,
        mask_id: str = "circle",
        feather: int = 0,
    ) -> Mask:
        """Build a circular mask (H, W) with an optional feathered edge."""
        yy, xx = np.mgrid[0:height, 0:width].astype(np.float64)
        cy = (height - 1) / 2 if cy is None else cy
        cx = (width - 1) / 2 if cx is None else cx
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        data = np.clip(radius - dist, 0.0, 1.0)
        data = np.clip(data / max(radius, 1e-6) * 2, 0.0, 1.0)
        if feather > 0:
            from modules.ai_video_studio.ai_compositor.matte_generator import feather_mask

            data = feather_mask(data[..., None], radius=feather)[..., 0]
        return cls(mask_id, data, {"shape": "circle"})


class MaskEngine:
    """Registry + application of masks."""

    def __init__(self) -> None:
        self._masks: dict[str, Mask] = {}

    def add(self, mask: Mask) -> MaskEngine:
        m = np.asarray(mask.data, dtype=np.float64)
        self._masks[mask.id] = Mask(mask.id, np.clip(m, 0.0, 1.0), mask.meta)
        return self

    def remove(self, mask_id: str) -> bool:
        return self._masks.pop(mask_id, None) is not None

    def get(self, mask_id: str) -> Mask:
        if mask_id not in self._masks:
            raise KeyError(f"unknown mask {mask_id!r}")
        return self._masks[mask_id]

    def apply(self, frame: NDArray[np.floating], mask_id: str, *, invert: bool = False) -> NDArray[np.floating]:
        m = self.get(mask_id).as_2d()
        if m.shape != frame.shape[:2]:
            from modules.ai_video_studio.editor_common import resize

            m = resize(m[..., None], frame.shape[1], frame.shape[0])[..., 0]
        if invert:
            m = 1.0 - m
        return np.clip(frame * m[..., None], 0.0, 1.0)

    def combine(self, mask_ids: list[str], *, operation: str = "union") -> NDArray[np.floating]:
        """Combine masks: union (max), intersect (min), difference."""
        layers = [self.get(i).as_2d() for i in mask_ids]
        if not layers:
            raise ValueError("no masks given")
        base = layers[0]
        for other in layers[1:]:
            if operation == "union":
                base = np.maximum(base, other)
            elif operation == "intersect":
                base = np.minimum(base, other)
            elif operation == "subtract":
                base = base - other
            else:
                raise ValueError(f"unknown operation {operation!r}")
        return np.clip(base, 0.0, 1.0)

    def ids(self) -> list[str]:
        return list(self._masks)

    def __len__(self) -> int:
        return len(self._masks)
