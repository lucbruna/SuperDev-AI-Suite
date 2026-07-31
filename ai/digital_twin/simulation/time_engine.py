"""Time engine."""

from __future__ import annotations


class TimeEngine:
    def __init__(self, start: float = 0.0, dt: float = 1.0) -> None:
        self._current = start
        self._dt = dt
        self._history: list[float] = []
        self._paused = False

    def advance(self) -> float:
        self._history.append(self._current)
        self._current += self._dt
        return self._current

    def advance_by(self, steps: int) -> list[float]:
        for _ in range(steps):
            self._history.append(self._current)
            self._current += self._dt
        return self._history[-steps:]

    def get_current(self) -> float:
        return self._current

    def get_dt(self) -> float:
        return self._dt

    def set_dt(self, dt: float) -> None:
        self._dt = dt

    def reset(self, start: float = 0.0) -> None:
        self._current = start
        self._history.clear()

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def is_paused(self) -> bool:
        return self._paused

    def get_history(self, limit: int = 100) -> list[float]:
        return self._history[-limit:]

    def elapsed(self) -> float:
        return self._current - (self._history[0] if self._history else 0)
