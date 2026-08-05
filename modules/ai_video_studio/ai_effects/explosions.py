"""Explosion effect — fireball, shockwave ring, and debris sparks.

Builds on the shared particle helpers in :mod:`ai_effects.effects_engine`.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from .effects_engine import (
    add_glow,
    draw_particles,
    make_fire_particles,
    make_spark_particles,
)


def apply(frame: Any, params: dict[str, Any] | None = None) -> NDArray[np.floating]:
    """Registry-compatible entry point for the explosion effect.

    ``params`` may carry ``x``/``y`` (normalized center), ``radius``
    (normalized), ``intensity`` and ``seed``.
    """
    p = params or {}
    return apply_explosion(
        frame,
        center=(float(p.get("x", 0.5)), float(p.get("y", 0.5))),
        radius=float(p.get("radius", 0.25)),
        intensity=float(p.get("intensity", 1.0)),
        seed=int(p.get("seed", 11)),
    )


def apply_explosion(
    frame: NDArray[np.floating],
    *,
    center: tuple[float, float],
    radius: float = 0.25,
    intensity: float = 1.0,
    seed: int = 11,
) -> NDArray[np.floating]:
    """Composite an explosion centered at ``center`` (normalized coords).

    The effect is deterministic given ``seed``.
    """
    h, w = frame.shape[:2]
    cx, cy = int(center[0] * w), int(center[1] * h)
    base_radius = int(radius * min(w, h))

    out = frame.astype(np.float64)

    # Shockwave ring: bright expanding circle
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ring_width = max(2, base_radius // 6)
    ring = np.exp(-((dist - base_radius) ** 2) / (2 * ring_width**2))
    ring_strength = 0.6 * intensity
    out[..., 0] += ring * ring_strength * 0.4
    out[..., 1] += ring * ring_strength * 0.7
    out[..., 2] += ring * ring_strength

    # Fireball core
    core = np.exp(-((dist / max(1, base_radius * 0.55)) ** 2))
    core_strength = 0.85 * intensity
    out[..., 0] += core * core_strength * 0.55
    out[..., 1] += core * core_strength * 0.75
    out[..., 2] += core * core_strength * 0.35

    # Particle layers
    rng = np.random.default_rng(seed)
    fire = make_fire_particles(
        n=60, frame_shape=(h, w), center=(cx, cy), rng=rng, spread=base_radius * 0.4
    )
    sparks = make_spark_particles(
        n=40, frame_shape=(h, w), center=(cx, cy), rng=rng, spread=base_radius
    )
    out = draw_particles(out, fire, radius=max(2, base_radius // 18), color=(1.0, 0.75, 0.35))
    out = draw_particles(out, sparks, radius=max(1, base_radius // 30), color=(1.0, 0.95, 0.6))

    out = add_glow(out, intensity=0.5 * intensity)
    return np.clip(out, 0.0, 1.0)
