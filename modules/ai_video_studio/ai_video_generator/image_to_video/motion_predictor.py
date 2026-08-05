"""Motion predictor — predict plausible motion from image content."""
from __future__ import annotations

from typing import Any


class MotionPredictor:
    """Guesses motion vectors for scene regions based on depth."""
    def predict(self, depth: dict[str, Any]) -> dict[str, Any]:
        motions = []
        for layer in depth.get("layers", []):
            # Deeper layers move less (parallax).
            scale = 1.0 - layer["depth"]
            motions.append(
                {
                    "layer": layer["name"],
                    "velocity": [round(0.5 * scale, 3), 0.0, round(0.2 * scale, 3)],
                    "direction": "right" if scale > 0.5 else "slow",
                }
            )
        return {"regions": motions, "confidence": 0.8}
