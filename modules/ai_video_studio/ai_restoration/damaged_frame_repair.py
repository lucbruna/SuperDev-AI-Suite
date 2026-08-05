"""Damaged frame repair — restores localized damage on a single frame.

Damage is located via per-channel outlier detection (values far from the
local median are assumed damaged), then filled by blending the median
with the temporal neighbors. Deterministic and dependency-light.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError


class DamagedFrameRepair:
    """Repairs damaged regions on frames using neighbor + median blending."""

    def __init__(self, median_size: int = 7, threshold: float = 3.0) -> None:
        self._median_size = max(3, int(median_size) | 1)  # odd kernel
        self._threshold = max(0.5, float(threshold))
        self._stats: dict[str, Any] = {"damaged_pixels": 0, "repaired": 0}

    # ── Public API ─────────────────────────────────────────────
    def repair_frame(
        self,
        frame: np.ndarray,
        neighbors: list[np.ndarray] | None = None,
        *,
        mask: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Repair ``frame``; returns (repaired, damage_mask_bool).

        ``neighbors`` (optional previous/next frames) improves the fill;
        without them a pure spatial median inpaint is used.
        """
        if frame.ndim != 3:
            raise ValidationError("repair_frame: frame must be HxWxC")
        h, w, c = frame.shape

        if mask is None:
            mask = self._detect_damage(frame)
        else:
            mask = mask.astype(bool)
            if mask.shape != (h, w):
                raise ValidationError("repair_frame: mask must be HxW")

        repaired = frame.copy().astype(np.float32)
        if not mask.any():
            self._stats = {"damaged_pixels": 0, "repaired": 0}
            return frame.copy(), mask

        # Spatial median of the current frame (robust background estimate)
        pad = self._median_size // 2
        padded = np.pad(frame, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
        median = np.zeros_like(frame, dtype=np.float32)
        for c_i in range(c):
            channel = padded[:, :, c_i]
            # Efficient rolling median via scipy if available, else manual
            try:
                from scipy.ndimage import median_filter

                median[:, :, c_i] = median_filter(
                    frame[:, :, c_i], size=self._median_size, mode="nearest"
                )
            except Exception:  # pragma: no cover — scipy optional
                hh, ww = channel.shape
                for y in range(pad, hh - pad):
                    for x in range(pad, ww - pad):
                        median[y - pad, x - pad, c_i] = float(
                            np.median(channel[y - pad : y + pad + 1, x - pad : x + pad + 1])
                        )

        # Temporal fill from neighbors
        temporal = None
        if neighbors:
            good = [n for n in neighbors if n is not None and n.shape == frame.shape]
            if good:
                temporal = np.mean(np.stack(good).astype(np.float32), axis=0)

        out = repaired
        if temporal is not None:
            out[mask] = temporal[mask]
            # Blend a small feather around the mask edge for seamlessness
            kernel = self._median_size
            soft = np.clip(self._feather(mask, kernel), 0.0, 1.0)[:, :, None]
            out = out * (1 - soft) + (temporal * soft + median * (1 - soft)) * soft
        else:
            out[mask] = median[mask]

        self._stats = {"damaged_pixels": int(mask.sum()), "repaired": int(mask.sum())}
        return np.clip(out, 0, 255).astype(frame.dtype), mask

    def detect_damage(self, frame: np.ndarray) -> np.ndarray:
        """Return a boolean mask of suspected damage."""
        return self._detect_damage(frame)

    def stats(self) -> dict[str, Any]:
        return dict(self._stats)

    # ── Internals ──────────────────────────────────────────────
    def _detect_damage(self, frame: np.ndarray) -> np.ndarray:
        pad = self._median_size // 2
        fp = frame.astype(np.float32)
        try:
            from scipy.ndimage import median_filter

            med = np.stack(
                [
                    median_filter(fp[:, :, i], size=self._median_size, mode="nearest")
                    for i in range(fp.shape[2])
                ],
                axis=-1,
            )
        except Exception:  # pragma: no cover
            med = np.zeros_like(fp)
            for c_i in range(fp.shape[2]):
                ch = np.pad(fp[:, :, c_i], ((pad, pad), (pad, pad)), mode="edge")
                hh, ww = ch.shape
                for y in range(pad, hh - pad):
                    for x in range(pad, ww - pad):
                        med[y - pad, x - pad, c_i] = np.median(
                            ch[y - pad : y + pad + 1, x - pad : x + pad + 1]
                        )

        dist = np.abs(fp - med).mean(axis=-1)
        # Normalize distance using local std (outlier z-score)
        local_std = np.sqrt(((fp - med) ** 2).mean(axis=-1)) + 1e-6
        z = dist / (local_std + 1e-6)
        mask = z > self._threshold
        # Morphological cleanup: keep only connected clusters > 3 px
        return self._clean_clusters(mask)

    def _clean_clusters(self, mask: np.ndarray, min_size: int = 3) -> np.ndarray:
        """Remove speckle — keep only clusters of at least ``min_size``."""
        labeled, count = self._label(mask)
        if count == 0:
            return np.zeros_like(mask)
        sizes = np.bincount(labeled.ravel())
        keep = np.zeros(count + 1, dtype=bool)
        keep[1:] = sizes[1:] >= min_size
        return keep[labeled]

    def _label(self, mask: np.ndarray) -> tuple[np.ndarray, int]:
        """Connected-components labeling via flood fill (deterministic)."""
        h, w = mask.shape
        labeled = np.zeros((h, w), dtype=np.int32)
        current = 0
        stack: list[tuple[int, int]] = []
        for y in range(h):
            for x in range(w):
                if mask[y, x] and labeled[y, x] == 0:
                    current += 1
                    stack.append((y, x))
                    labeled[y, x] = current
                    while stack:
                        cy, cx = stack.pop()
                        for ny, nx in (
                            (cy - 1, cx),
                            (cy + 1, cx),
                            (cy, cx - 1),
                            (cy, cx + 1),
                        ):
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and labeled[ny, nx] == 0:
                                labeled[ny, nx] = current
                                stack.append((ny, nx))
        return labeled, current

    def _feather(self, mask: np.ndarray, radius: int) -> np.ndarray:
        """Approximate feather by iterative dilation averaging."""
        soft = mask.astype(np.float32)
        for _ in range(max(1, radius // 2)):
            soft = self._dilate_mean(soft)
        return soft

    def _dilate_mean(self, arr: np.ndarray) -> np.ndarray:
        h, w = arr.shape
        padded = np.pad(arr, 1, mode="edge")
        out = np.zeros_like(arr)
        for y in range(h):
            for x in range(w):
                out[y, x] = padded[y : y + 3, x : x + 3].mean()
        return out


damaged_frame_repair = DamagedFrameRepair()
