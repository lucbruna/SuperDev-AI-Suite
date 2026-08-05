"""Motion tracking — dense-ish feature displacement between frames."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class MotionTracker:
    """Tracks a grid of feature points across two frames via block matching."""

    def __init__(self, grid: int = 8, block: int = 16, window: int = 8) -> None:
        self._grid = grid
        self._block = block
        self._window = window

    def compute_flow(self, a: NDArray[np.floating], b: NDArray[np.floating]) -> dict:
        """Return sparse optical flow between frames a and b."""
        ga = a.mean(axis=-1).astype(np.float64)
        gb = b.mean(axis=-1).astype(np.float64)
        h, w = ga.shape
        step = max(1, h // self._grid)
        block = min(self._block, min(h, w) // 4)
        win = self._window
        points, vectors = [], []
        for y in range(block, h - block, step):
            for x in range(block, w - block, step):
                tpl = ga[y - block : y + block, x - block : x + block]
                y0, y1 = max(0, y - win), min(h - block, y + win)
                x0, x1 = max(0, x - win), min(w - block, x + win)
                best, best_disp = 1e9, (0.0, 0.0)
                for dy in range(y0, y1 - 2 * block + 1, 2):
                    for dx in range(x0, x1 - 2 * block + 1, 2):
                        patch = gb[dy : dy + 2 * block, dx : dx + 2 * block]
                        if patch.shape != tpl.shape:
                            continue
                        err = np.abs(patch - tpl).mean()
                        if err < best:
                            best = err
                            best_disp = (float(x + block - (dx + block)), float(y + block - (dy + block)))
                points.append({"x": float(x), "y": float(y)})
                vectors.append({"dx": best_disp[0], "dy": best_disp[1]})
        return {"points": points, "vectors": vectors, "count": len(points)}

    def track(self, frames: list[NDArray[np.floating]]) -> list[dict]:
        out = []
        for a, b in zip(frames, frames[1:], strict=False):
            out.append(self.compute_flow(a, b))
        return out

    def __call__(self, frame: NDArray[np.floating]) -> list[dict]:
        """Per-frame interface for the tracking engine: compare against the
        previous frame and report the flow as a lightweight detection."""
        if self._prev is None:
            self._prev = frame
            return []
        flow = self.compute_flow(self._prev, frame)
        self._prev = frame
        return [{"kind": "motion", **flow}]

    _prev: NDArray[np.floating] | None = None
