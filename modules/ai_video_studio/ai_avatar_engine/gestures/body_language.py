"""Body language — posture and stance vocabulary."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Posture:
    """A full-body posture (lean, arm energy, stance width)."""

    name: str
    lean: float = 0.0
    arm_energy: float = 0.3
    stance: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "lean": self.lean, "arm_energy": self.arm_energy,
                "stance": self.stance}


POSTURES = [
    Posture("confident_stance", 0.2, 0.5, 0.6),
    Posture("open_stance", 0.0, 0.6, 0.7),
    Posture("nervous_stance", -0.3, 0.2, 0.3),
    Posture("authoritative", 0.3, 0.7, 0.6),
    Posture("welcoming", 0.0, 0.5, 0.5),
]


def postures() -> list[Posture]:
    return POSTURES
