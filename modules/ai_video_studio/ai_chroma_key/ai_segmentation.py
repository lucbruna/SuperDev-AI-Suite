"""AI segmentation — pluggable model interface with a heuristic fallback.

When no model is configured, falls back to a chroma matte so pipelines keep
working end-to-end.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import NDArray


@dataclass
class SegmentationModel:
    """Duck-typed model wrapper: ``predict(frame) -> matte``."""

    predict: Callable[[NDArray[np.floating]], NDArray[np.floating]]
    name: str = "custom"


class AISegmentation:
    """Runs an optional segmentation model, falling back to chroma keying."""

    def __init__(self, model: SegmentationModel | None = None) -> None:
        self._model = model

    def set_model(self, model: SegmentationModel) -> None:
        self._model = model

    def segment(
        self,
        frame: NDArray[np.floating],
        *,
        fallback_screen: str = "green",
        tolerance: float = 0.35,
    ) -> NDArray[np.floating]:
        if self._model is not None:
            matte = np.asarray(self._model.predict(frame), dtype=np.float64)
            if matte.ndim == 3:
                matte = matte[..., 0]
            return np.clip(matte, 0.0, 1.0)
        # Heuristic fallback: central-subject saliency via chroma difference
        from ..ai_compositor.matte_generator import chroma_matte

        key = (0.0, 0.9, 0.0) if fallback_screen == "green" else (0.0, 0.3, 0.9)
        return chroma_matte(frame, key_color=key, tolerance=tolerance, softness=0.15)
