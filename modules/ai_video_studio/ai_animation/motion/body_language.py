"""Body language — posture and attitude animation layer."""
from __future__ import annotations

from typing import Any

_POSTURES = {
    "confident": {"shoulders": "back", "lean": 0.05, "open": 0.8},
    "nervous": {"shoulders": "forward", "lean": -0.1, "open": 0.3},
    "relaxed": {"shoulders": "neutral", "lean": 0.0, "open": 0.6},
    "tired": {"shoulders": "slump", "lean": -0.15, "open": 0.2},
}


class BodyLanguage:
    """Maps attitudes to body posture parameters."""

    def posture(self, attitude: str = "relaxed") -> dict[str, Any]:
        if attitude not in _POSTURES:
            raise ValueError(f"Unknown attitude '{attitude}'")
        return dict(_POSTURES[attitude])

    def available_attitudes(self) -> list[str]:
        return list(_POSTURES.keys())
