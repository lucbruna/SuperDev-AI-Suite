"""Cinematic camera — film grammar camera moves."""
from __future__ import annotations

from typing import Any

_MOVES = ("static", "dolly_in", "dolly_out", "track", "crane_up", "crane_down", "push_in")


class CinematicCamera:
    """Applies cinematic moves with eased motion curves."""

    def move(self, move: str, t: float) -> dict[str, Any]:
        if move not in _MOVES:
            raise ValueError(f"Unknown move '{move}'")
        eased = t * t * (3 - 2 * t)  # smoothstep
        base: dict[str, Any] = {"move": move, "t": round(t, 4)}
        if move == "dolly_in":
            base["zoom"] = round(1.0 + eased * 0.4, 4)
        elif move == "dolly_out":
            base["zoom"] = round(1.4 - eased * 0.4, 4)
        elif move == "track":
            base["dx"] = round(eased * 0.5, 4)
        elif move == "crane_up":
            base["dy"] = round(eased * 0.4, 4)
        elif move == "crane_down":
            base["dy"] = round(-eased * 0.4, 4)
        elif move == "push_in":
            base["zoom"] = round(1.0 + eased * 0.6, 4)
        else:
            base["zoom"] = 1.0
        return base

    def available_moves(self) -> list[str]:
        return list(_MOVES)
