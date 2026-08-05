"""Prediction: deterministic linear extrapolation over mirrored snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.digital_twin.state_mirror import Snapshot


@dataclass
class Prediction:
    entity_id: str
    horizon: int
    steps: list[dict[str, Any]] = field(default_factory=list)
    method: str = "linear"

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "horizon": self.horizon,
            "method": self.method,
            "steps": [dict(step) for step in self.steps],
        }


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class Predictor:
    """Extrapolates numeric attributes from the last two snapshots.

    For each numeric key the per-step delta is derived from the most recent
    two snapshots; non-numeric values carry forward unchanged.
    """

    def predict(self, history: list[Snapshot], horizon: int) -> Prediction:
        entity_id = history[-1].entity_id if history else ""
        if not history or horizon <= 0:
            return Prediction(entity_id=entity_id, horizon=max(0, horizon))
        latest = history[-1].state
        if len(history) >= 2:
            prev = history[-2].state
            deltas = {
                key: latest[key] - prev[key]
                for key in latest
                if _is_number(latest[key]) and _is_number(prev.get(key))
            }
        else:
            deltas = {}
        steps: list[dict[str, Any]] = []
        current = dict(latest)
        for _ in range(horizon):
            projected: dict[str, Any] = {}
            for key, value in current.items():
                if _is_number(value) and key in deltas:
                    projected[key] = round(value + deltas[key], 6)
                else:
                    projected[key] = value
            current = projected
            steps.append(projected)
        return Prediction(entity_id=entity_id, horizon=horizon, steps=steps)
