"""Eye tracking — locate pupils (dark spots) inside a face region."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class EyeTracker:
    """Given a face bbox, finds the two darkest elliptical regions (eyes)."""

    def __call__(self, frame: NDArray[np.floating], face: dict) -> list[dict]:
        h, w = frame.shape[:2]
        fx = int(face["x"] - face.get("w", 0) / 2)
        fy = int(face["y"] - face.get("h", 0) / 2)
        fw = int(face.get("w", 0))
        fh = int(face.get("h", 0))
        x0, y0 = max(0, fx), max(0, fy)
        x1, y1 = min(w, fx + fw), min(h, fy + fh)
        if x1 <= x0 or y1 <= y0:
            return []
        region = frame[y0:y1, x0:x1]
        luma = region.mean(axis=-1)
        # Eyes live in the upper third of the face
        upper = luma[: max(1, luma.shape[0] // 3)]
        dark = upper < np.percentile(upper, 25)
        results = []
        for band in (dark[:, : dark.shape[1] // 2], dark[:, dark.shape[1] // 2 :]):
            ys, xs = np.where(band)
            if len(xs) == 0:
                continue
            bx = x0 + (xs.mean() + (dark.shape[1] // 2 if band is dark[:, dark.shape[1] // 2 :] else 0))
            by = y0 + ys.mean()
            results.append({"x": float(bx), "y": float(by), "kind": "eye"})
        return results

    def track(self, frame: NDArray[np.floating], faces: list[dict]) -> list[dict]:
        out: list[dict] = []
        for face in faces:
            out.extend(self.__call__(frame, face))
        return out
