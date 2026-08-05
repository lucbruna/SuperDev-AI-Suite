"""Shared primitives for the Volume 5 professional editing subsystems.

Kept free of heavy dependencies beyond numpy/PIL/ffmpeg (already used across
the studio's media toolkit) so every subsystem builds on one foundation:
numeric helpers, frame coercion, logging, ffmpeg execution, registries,
incremental stats and a bounded undo/redo stack.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Any, Callable

import numpy as np


# ── Numeric helpers ──────────────────────────────────────────────
def box_filter(arr: np.ndarray, kernel: int) -> np.ndarray:
    """Fast separable box blur (kernel x kernel) with edge padding.

    Used for feathered masks and cheap smoothing. ``kernel`` is clamped to
    an odd value >= 1.
    """
    k = max(1, int(kernel) | 1)
    if k == 1:
        return arr.copy()
    out = arr.astype(np.float64)
    h, w = out.shape[:2]
    kern = np.ones((k,), dtype=np.float64) / k

    def _line_conv(line: np.ndarray) -> np.ndarray:
        padded = np.pad(line, (k // 2, k // 2), mode="edge")
        return np.convolve(padded, kern, mode="valid")

    if out.ndim == 2:
        out = np.apply_along_axis(_line_conv, 1, out)  # horizontal
        out = np.apply_along_axis(_line_conv, 0, out)  # vertical
    else:
        for c in range(out.shape[2]):
            out[:, :, c] = np.apply_along_axis(_line_conv, 1, out[:, :, c])
            out[:, :, c] = np.apply_along_axis(_line_conv, 0, out[:, :, c])
    return out


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp ``value`` to the inclusive [lo, hi] range."""
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b, with t clamped to [0, 1]."""
    return a + (b - a) * clamp(t)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Hermite smoothstep — 0 before edge0, 1 after edge1."""
    t = clamp((x - edge0) / max(1e-9, (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def mix(a: float, b: float, t: float) -> float:
    """Alias of lerp for readability in blend/shader code."""
    return lerp(a, b, t)


# ── Frame helpers ────────────────────────────────────────────────
def as_rgb(frame: Any) -> np.ndarray:
    """Coerce any frame-like input to a contiguous HxWx3 uint8 array."""
    arr = np.asarray(frame)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    if arr.shape[-1] == 4:
        arr = arr[..., :3]
    return np.ascontiguousarray(arr[..., :3], dtype=np.uint8)


def resize_frame(frame: Any, width: int, height: int) -> np.ndarray:
    """Bilinear resize via Pillow, returning a HxWx3 uint8 array."""
    from PIL import Image

    img = Image.fromarray(as_rgb(frame)).resize((width, height), Image.BILINEAR)
    return np.asarray(img, dtype=np.uint8)


# Backwards-compatible alias used by the compositor / chroma-key / mask
# subsystems (they historically imported ``resize`` from editor_common).
resize = resize_frame


def frame_to_png(frame: Any, output_path: str) -> str:
    """Persist a single frame as PNG (useful for previews and scopes)."""
    from PIL import Image

    from pathlib import Path

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(as_rgb(frame)).save(out, format="PNG")
    return str(out)


# ── Logging ──────────────────────────────────────────────────────
def make_logger(name: str) -> logging.Logger:
    """Module-scoped logger under the ``ai_video_studio`` namespace."""
    return logging.getLogger(f"ai_video_studio.{name}")


# ── FFmpeg ───────────────────────────────────────────────────────
def ffmpeg_available() -> bool:
    """True when an ffmpeg binary is on PATH."""
    return shutil.which("ffmpeg") is not None


def run_ffmpeg(cmd: list[str], timeout: float = 600.0) -> str:
    """Run an ffmpeg command, returning stderr; raise on non-zero exit."""
    if not ffmpeg_available():
        raise RuntimeError("ffmpeg is not installed")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        from modules.ai_video_studio.core.exceptions import FFmpegError

        raise FFmpegError(" ".join(cmd), proc.stderr or "unknown error")
    return proc.stderr or ""


# ── Registry ─────────────────────────────────────────────────────
class Registry:
    """Named callable registry (effects, LUTs, export formats, trackers)."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._items: dict[str, Callable[..., Any]] = {}
        self._meta: dict[str, dict[str, Any]] = {}

    def register(self, key: str, fn: Callable[..., Any], **meta: Any) -> None:
        """Register ``fn`` under ``key`` with optional metadata."""
        self._items[key] = fn
        self._meta[key] = meta

    def get(self, key: str) -> Callable[..., Any]:
        if key not in self._items:
            raise KeyError(
                f"Unknown {self.name}: '{key}' (available: {', '.join(sorted(self._items))})"
            )
        return self._items[key]

    def names(self) -> list[str]:
        return sorted(self._items)

    def meta(self, key: str) -> dict[str, Any]:
        return self._meta.get(key, {})

    def has(self, key: str) -> bool:
        return key in self._items

    def __len__(self) -> int:
        return len(self._items)


# ── Stats ────────────────────────────────────────────────────────
class StatTracker:
    """Incremental min/max/avg/count tracker for performance stats."""

    def __init__(self) -> None:
        self.count = 0
        self.total = 0.0
        self._min: float | None = None
        self._max: float | None = None

    def push(self, value: float) -> None:
        self.count += 1
        self.total += value
        self._min = value if self._min is None else min(self._min, value)
        self._max = value if self._max is None else max(self._max, value)

    def stats(self) -> dict[str, float]:
        return {
            "count": self.count,
            "min": self._min if self._min is not None else 0.0,
            "max": self._max if self._max is not None else 0.0,
            "avg": (self.total / self.count) if self.count else 0.0,
        }


# ── Undo / Redo ──────────────────────────────────────────────────
class UndoStack:
    """Bounded command stack with undo/redo support (snapshots of state)."""

    def __init__(self, limit: int = 100) -> None:
        self._undo: list[Any] = []
        self._redo: list[Any] = []
        self.limit = max(1, limit)

    def push(self, state: Any) -> None:
        self._undo.append(state)
        if len(self._undo) > self.limit:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self) -> Any | None:
        """Pop the previous snapshot (or None when nothing to undo)."""
        if not self._undo:
            return None
        current = self._undo.pop()
        self._redo.append(current)
        return self._undo[-1] if self._undo else None

    def redo(self) -> Any | None:
        if not self._redo:
            return None
        state = self._redo.pop()
        self._undo.append(state)
        return state

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()
