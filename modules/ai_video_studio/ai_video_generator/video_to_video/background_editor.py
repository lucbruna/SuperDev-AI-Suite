"""Background editor — replace or blur backgrounds in video."""
from __future__ import annotations

from typing import Any


class BackgroundEditor:
    """Performs background replacement or blur via segmentation masks."""

    def replace(self, source: str, *, background: str, keep_foreground: str = "person") -> dict[str, Any]:
        return {
            "source": source,
            "operation": "replace",
            "background": background,
            "keep_foreground": keep_foreground,
            "segmentation_model": "sam2",
        }

    def blur(self, source: str, *, strength: float = 0.5) -> dict[str, Any]:
        return {"source": source, "operation": "blur", "strength": strength, "mask": "background"}
