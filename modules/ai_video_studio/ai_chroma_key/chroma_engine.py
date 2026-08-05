"""Chroma key engine — full pipeline: key → despill → refine → composite."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ..ai_compositor import matte_generator
from .background_replacement import replace_background
from .spill_suppressor import suppress_spill


@dataclass
class ChromaResult:
    foreground: NDArray[np.floating]
    matte: NDArray[np.floating]
    background: NDArray[np.floating] | None = None
    meta: dict[str, Any] = field(default_factory=dict)


class ChromaKeyEngine:
    """Deterministic chroma key pipeline over float frames."""

    def key(
        self,
        frame: NDArray[np.floating],
        *,
        screen: str = "green",
        tolerance: float = 0.35,
        softness: float = 0.12,
        despill: float = 0.5,
        refine: int = 1,
    ) -> ChromaResult:
        key_color = {"green": (0.0, 0.9, 0.0), "blue": (0.0, 0.3, 0.9)}[screen]
        matte = matte_generator.chroma_matte(
            frame,
            key_color=key_color,
            tolerance=tolerance,
            softness=softness,
        )
        if refine > 0:
            matte = matte_generator.feather_mask(matte[..., None], radius=refine)[..., 0]
        fg = frame[..., :3] * matte[..., None]
        if despill > 0:
            fg = suppress_spill(fg, matte, key_color=key_color, amount=despill)
        return ChromaResult(
            foreground=np.clip(fg, 0.0, 1.0),
            matte=matte,
            meta={"screen": screen, "tolerance": tolerance},
        )

    def composite(
        self,
        frame: NDArray[np.floating],
        background: NDArray[np.floating],
        **kwargs: Any,
    ) -> NDArray[np.floating]:
        result = self.key(frame, **kwargs)
        return replace_background(frame, result.matte, background)

    def stats(self) -> dict:
        return {"pipeline": ["key", "despill", "refine", "composite"]}
