"""FPS reconstruction — rebuild missing/damaged frames via temporal interpolation.

Uses simple block-matching motion compensation to keep interpolation
scene-aware (does not blur across cuts) while staying dependency-light.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError


class FPSReconstruction:
    """Reconstructs frames so a clip plays at a target FPS."""

    def __init__(self, block_size: int = 16, search_radius: int = 8) -> None:
        self._block_size = max(4, int(block_size))
        self._search_radius = max(1, int(search_radius))
        self._stats: dict[str, Any] = {"rebuilt": 0, "interpolated": 0, "skipped": 0}

    # ── Public API ─────────────────────────────────────────────
    def reconstruct(
        self,
        frames: list[np.ndarray],
        source_fps: float,
        target_fps: float,
        *,
        fill_missing: bool = True,
    ) -> tuple[list[np.ndarray], dict[str, Any]]:
        """Resample ``frames`` from ``source_fps`` to ``target_fps``.

        Handles both densification (interpolation) and decimation
        (frame dropping). ``None`` entries in ``frames`` are treated as
        missing frames and rebuilt by interpolation.
        """
        if not frames:
            raise ValidationError("reconstruct: no frames provided")
        if source_fps <= 0 or target_fps <= 0:
            raise ValidationError("reconstruct: FPS values must be positive")

        validated = [f for f in frames if f is not None]
        if not validated:
            raise ValidationError("reconstruct: all frames are missing")
        ref = validated[0]
        if ref.ndim != 3:
            raise ValidationError("reconstruct: frames must be HxWxC arrays")

        self._stats = {"rebuilt": 0, "interpolated": 0, "skipped": 0}
        frame_list: list[np.ndarray] = [f if f is not None else ref.copy() for f in frames]

        # 1) Rebuild missing frames in place
        if fill_missing:
            frame_list = self._fill_gaps(frame_list)

        # 2) Resample to target FPS
        n = len(frame_list)
        if n == 1:
            return [frame_list[0]], dict(self._stats)

        ratio = target_fps / source_fps
        if ratio < 1.0:
            # Decimation — pick exact frames
            indices = np.linspace(0, n - 1, max(1, int(round(n * ratio))))
            out = [frame_list[int(round(i))] for i in indices]
            self._stats["skipped"] = n - len(out)
            return out, dict(self._stats)

        # Densification — interpolate between neighbors at exact time steps
        out_frames: list[np.ndarray] = []
        for t in np.arange(0, n - 1, 1.0 / ratio):
            base = int(np.floor(t))
            frac = min(1.0, t - base)
            nxt = frame_list[min(base + 1, n - 1)]
            if frac < 1e-6:
                out_frames.append(frame_list[base].copy())
            else:
                out_frames.append(self._motion_blend(frame_list[base], nxt, frac))
                self._stats["interpolated"] += 1
        out_frames.append(frame_list[-1].copy())
        return out_frames, dict(self._stats)

    def rebuild_frame(
        self, frames: list[np.ndarray | None], index: int
    ) -> np.ndarray:
        """Rebuild a single missing frame from its temporal neighbors."""
        n = len(frames)
        if not 0 <= index < n:
            raise ValidationError(f"rebuild_frame: index {index} out of range 0..{n - 1}")
        if frames[index] is not None:
            raise ValidationError("rebuild_frame: frame at index is present")

        left = next((f for f in reversed(frames[:index]) if f is not None), None)
        right = next((f for f in frames[index + 1 :] if f is not None), None)
        if left is None and right is None:
            raise ValidationError("rebuild_frame: no neighbors to interpolate from")
        if left is None:
            return right.copy()
        if right is None:
            return left.copy()

        # Motion-compensated midpoint
        return self._motion_blend(left, right, 0.5)

    def stats(self) -> dict[str, Any]:
        """Return counters from the last reconstruction run."""
        return dict(self._stats)

    # ── Internals ──────────────────────────────────────────────
    def _fill_gaps(self, frames: list[np.ndarray]) -> list[np.ndarray]:
        out: list[np.ndarray] = []
        for i, frame in enumerate(frames):
            if frame is not None:
                out.append(frame)
                continue
            self._stats["rebuilt"] += 1
            left = next((f for f in reversed(out) if f is not None), None)
            right = next((f for f in frames[i + 1 :] if f is not None), None)
            if left is None and right is None:
                out.append(frames[i])  # unreachable: placeholder
            elif left is None:
                out.append(right.copy())
            elif right is None:
                out.append(left.copy())
            else:
                out.append(self._motion_blend(left, right, 0.5))
        return out

    def _motion_blend(self, a: np.ndarray, b: np.ndarray, frac: float) -> np.ndarray:
        """Blend a→b at ``frac``, warping b by coarse block motion."""
        fa, fb = a.astype(np.float32), b.astype(np.float32)
        h, w = a.shape[:2]
        if h < 2 * self._block_size or w < 2 * self._block_size:
            return (fa * (1 - frac) + fb * frac).astype(a.dtype)

        # Downscale for block matching speed
        scale = 0.25
        sh, sw = max(2, int(h * scale)), max(2, int(w * scale))
        sa = self._resize(fa, sh, sw)
        sb = self._resize(fb, sh, sw)
        flow = self._block_flow(sa, sb)  # (dy, dx) grid

        # Warp b (full res) by the upscaled flow field
        warped = self._warp_by_flow(fb, flow, sh, sw)
        return (fa * (1 - frac) + warped * frac).astype(a.dtype)

    def _resize(self, img: np.ndarray, sh: int, sw: int) -> np.ndarray:
        h, w = img.shape[:2]
        yy = (np.arange(sh) * (h - 1) / max(sh - 1, 1)).astype(np.int32)
        xx = (np.arange(sw) * (w - 1) / max(sw - 1, 1)).astype(np.int32)
        return img[yy][:, xx]

    def _block_flow(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Coarse block-matching flow field as (dy, dx) arrays over a grid."""
        h, w = a.shape[:2]
        bs = self._block_size
        gy = np.arange(0, h - bs + 1, bs)
        gx = np.arange(0, w - bs + 1, bs)
        flow_y = np.zeros((len(gy), len(gx)), dtype=np.float32)
        flow_x = np.zeros_like(flow_y)
        best = np.full(flow_y.shape, np.inf, dtype=np.float32)

        grays_a = a[:, :, :3].mean(axis=2)
        grays_b = b[:, :, :3].mean(axis=2)

        for dy in range(-self._search_radius, self._search_radius + 1):
            for dx in range(-self._search_radius, self._search_radius + 1):
                cost = np.zeros_like(best)
                for iy, y in enumerate(gy):
                    for ix, x in enumerate(gx):
                        blk_a = grays_a[y : y + bs, x : x + bs]
                        ny = min(max(y + dy, 0), h - bs)
                        nx = min(max(x + dx, 0), w - bs)
                        blk_b = grays_b[ny : ny + bs, nx : nx + bs]
                        cost[iy, ix] = np.abs(blk_a - blk_b).mean()
                better = cost < best
                best[better] = cost[better]
                flow_y[better] = dy
                flow_x[better] = dx
        return flow_y, flow_x

    def _warp_by_flow(
        self, img: np.ndarray, flow: tuple[np.ndarray, np.ndarray], sh: int, sw: int
    ) -> np.ndarray:
        """Bilinear-warp ``img`` by a flow grid upscaled to full resolution."""
        h, w = img.shape[:2]
        flow_y, flow_x = flow
        gy = np.linspace(0, h - 1, flow_y.shape[0])
        gx = np.linspace(0, w - 1, flow_y.shape[1])

        # Interpolate the flow grid to full resolution (bilinear via interp)
        fy = np.empty(h, dtype=np.float32)
        fx = np.empty(w, dtype=np.float32)
        for i in range(flow_y.shape[1]):
            fy += np.interp(np.arange(h), gy, flow_y[:, i]) / flow_y.shape[1]
        for j in range(flow_x.shape[0]):
            fx += np.interp(np.arange(w), gx, flow_x[j]) / flow_x.shape[0]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        sy = np.clip(yy + fy[:, None], 0, h - 1)
        sx = np.clip(xx + fx[None, :], 0, w - 1)

        yi = np.clip(sy.astype(np.int32), 0, h - 2)
        xi = np.clip(sx.astype(np.int32), 0, w - 2)
        dyf = sy - yi
        dxf = sx - xi

        out = np.empty_like(img, dtype=np.float32)
        for c in range(img.shape[2]):
            ch = img[:, :, c]
            w0 = ch[yi, xi]
            w1 = ch[yi, xi + 1]
            w2 = ch[yi + 1, xi]
            w3 = ch[yi + 1, xi + 1]
            out[:, :, c] = (
                w0 * (1 - dxf) * (1 - dyf)
                + w1 * dxf * (1 - dyf)
                + w2 * (1 - dxf) * dyf
                + w3 * dxf * dyf
            )
        return out


fps_reconstruction = FPSReconstruction()
