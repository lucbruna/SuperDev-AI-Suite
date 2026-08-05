"""Simulator: deterministic state-transition simulation over N steps."""
from __future__ import annotations

from typing import Any, Callable

from aios.digital_twin.entity import TwinEntity

#: transition: (state, step) -> new state dict
TransitionFn = Callable[[dict[str, Any], int], dict[str, Any]]


class Simulator:
    """Advances a copy of the entity state with a pure transition function."""

    def simulate(
        self, entity: TwinEntity, transition: TransitionFn, steps: int
    ) -> list[dict[str, Any]]:
        """Return ``steps`` predicted states; the entity itself is untouched."""
        state = dict(entity.state)
        projected: list[dict[str, Any]] = []
        for step in range(1, steps + 1):
            state = dict(transition(state, step))
            projected.append(state)
        return projected

    def run(
        self, entity: TwinEntity, transition: TransitionFn, steps: int
    ) -> list[dict[str, Any]]:
        """Alias of :meth:`simulate`."""
        return self.simulate(entity, transition, steps)
