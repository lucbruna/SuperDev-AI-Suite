"""Collision engine — detect and resolve collisions between bodies."""
from __future__ import annotations

import math
from typing import Any


class CollisionEngine:
    """Sphere-vs-sphere and sphere-vs-plane collision checks."""

    def sphere_sphere(
        self,
        a: tuple[float, float, float],
        b: tuple[float, float, float],
        radius_a: float,
        radius_b: float,
    ) -> dict[str, Any]:
        dist = math.dist(a, b)
        hit = dist <= radius_a + radius_b
        return {"collided": hit, "distance": round(dist, 4), "penetration": round(max(0.0, radius_a + radius_b - dist), 4)}

    def sphere_plane(
        self,
        sphere: tuple[float, float, float],
        radius: float,
        plane_y: float = 0.0,
    ) -> dict[str, Any]:
        dist = sphere[1] - plane_y
        hit = dist <= radius
        return {"collided": hit, "height_above_plane": round(dist, 4)}

    def resolve(
        self,
        a: dict[str, Any],
        b: dict[str, Any],
        *,
        restitution: float = 0.5,
    ) -> dict[str, Any]:
        va = a["velocity"]
        vb = b["velocity"]
        va_new = [v * (1 - restitution) for v in va]
        vb_new = [v * restitution for v in vb]
        return {"a_velocity": va_new, "b_velocity": vb_new, "restitution": restitution}
