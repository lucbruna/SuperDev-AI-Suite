"""Rigid body — rigid-body dynamics integration."""
from __future__ import annotations

class RigidBody:
    """A rigid body with position, velocity, mass and restitution."""

    def __init__(
        self,
        *,
        mass: float = 1.0,
        position: tuple[float, float, float] = (0, 0, 0),
        restitution: float = 0.5,
    ) -> None:
        if mass <= 0:
            raise ValueError("mass must be positive")
        self.mass = mass
        self.position = list(position)
        self.velocity = [0.0, 0.0, 0.0]
        self.restitution = restitution

    def apply_force(self, force: tuple[float, float, float], dt: float) -> None:
        for axis in range(3):
            self.velocity[axis] += force[axis] / self.mass * dt

    def integrate(self, dt: float) -> tuple[float, float, float]:
        for axis in range(3):
            self.position[axis] += self.velocity[axis] * dt
        return tuple(self.position)

    def kinetic_energy(self) -> float:
        speed_sq = sum(v * v for v in self.velocity)
        return 0.5 * self.mass * speed_sq
