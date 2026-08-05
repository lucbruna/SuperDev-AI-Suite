"""Virtual camera — a camera instance with position, target and lens."""
from __future__ import annotations

from typing import Any


class VirtualCamera:
    """Represents a virtual camera in 3D scene space."""

    def __init__(
        self,
        *,
        position: tuple[float, float, float] = (0, 1.6, 5.0),
        target: tuple[float, float, float] = (0, 1.6, 0.0),
        focal_length: float = 50.0,
        sensor_width: float = 36.0,
    ) -> None:
        self.position = position
        self.target = target
        self.focal_length = focal_length
        self.sensor_width = sensor_width

    def look_at(self, target: tuple[float, float, float]) -> None:
        self.target = target

    def move_to(self, position: tuple[float, float, float]) -> None:
        self.position = position

    def set_focal(self, focal_length: float) -> None:
        if focal_length <= 0:
            raise ValueError("focal_length must be positive")
        self.focal_length = focal_length

    def horizontal_fov(self) -> float:
        import math

        return round(math.degrees(2 * math.atan(self.sensor_width / (2 * self.focal_length))), 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": list(self.position),
            "target": list(self.target),
            "focal_length": self.focal_length,
            "sensor_width": self.sensor_width,
            "h_fov_deg": self.horizontal_fov(),
        }
