"""Simulator."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Simulator:
    def __init__(self) -> None:
        self._models: dict[str, Callable] = {}
        self._state: dict[str, Any] = {}

    def register(self, name: str, model_fn: Callable) -> dict[str, Any]:
        self._models[name] = model_fn
        return {"name": name, "registered": True}

    def set_state(self, state: dict[str, Any]) -> None:
        self._state.update(state)

    def get_state(self) -> dict[str, Any]:
        return dict(self._state)

    def step(self) -> dict[str, Any]:
        new_state = {}
        for name, model_fn in self._models.items():
            try:
                new_state[name] = model_fn(self._state)
            except Exception as e:
                new_state[name] = {"error": str(e)}
        self._state.update(new_state)
        return new_state

    def run(self, steps: int) -> list[dict[str, Any]]:
        history = []
        for _ in range(steps):
            history.append(self.step())
        return history

    def reset(self, initial_state: dict[str, Any] = None) -> None:
        self._state = initial_state or {}

    def list_models(self) -> list[str]:
        return list(self._models.keys())

    def state_size(self) -> int:
        return len(self._state)
