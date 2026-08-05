"""Marker tracking — detect high-contrast fiducial markers (QR/ArUco-like)."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class MarkerTracker:
    """Finds dark-square markers (bright surround) and returns their corners."""

    def find_markers(self, frame: NDArray[np.floating], *, size: int = 24) -> list[dict]:
        f = frame.astype(np.float64)
        luma = f.mean(axis=-1)
        h, w = luma.shape
        markers: list[dict] = []
        step = max(1, size // 2)
        for y in range(0, h - size, step):
            for x in range(0, w - size, step):
                cell = luma[y : y + size, x : x + size]
                center = cell[size // 4 : 3 * size // 4, size // 4 : 3 * size // 4]
                border = np.concatenate([cell[0], cell[-1], cell[:, 0], cell[:, -1]])
                if border.mean() > 0.8 and center.mean() < 0.2:
                    markers.append(
                        {
                            "x": float(x + size / 2),
                            "y": float(y + size / 2),
                            "size": float(size),
                            "corners": [
                                {"x": float(x), "y": float(y)},
                                {"x": float(x + size), "y": float(y)},
                                {"x": float(x + size), "y": float(y + size)},
                                {"x": float(x), "y": float(y + size)},
                            ],
                            "kind": "marker",
                        }
                    )
        # Merge overlapping detections
        merged: list[dict] = []
        for m in markers:
            if any(_overlap(m, prev) for prev in merged):
                continue
            merged.append(m)
        return merged[:16]

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        return self.find_markers(frame)


def _overlap(a: dict, b: dict, tol: float = 0.6) -> bool:
    return abs(a["x"] - b["x"]) < a["size"] * tol and abs(a["y"] - b["y"]) < a["size"] * tol
