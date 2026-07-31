"""Policy gates for actions: rate limits, allow/deny lists, cooldown."""

from __future__ import annotations

import time
from typing import Any


class ActionPolicy:
    """Guards action execution with configurable constraints."""

    def __init__(self, max_calls_per_window: int = 100,
                 window_seconds: float = 60.0,
                 cooldown_seconds: float = 0.0,
                 allowlist: list[str] | None = None,
                 denylist: list[str] | None = None) -> None:
        self.max_calls = max_calls_per_window
        self.window = window_seconds
        self.cooldown = cooldown_seconds
        self._allowlist: set[str] = set(allowlist or [])
        self._denylist: set[str] = set(denylist or [])
        self._calls: dict[str, list[float]] = {}
        self._last: dict[str, float] = {}

    def allow(self, action_id: str) -> None:
        self._allowlist.add(action_id)

    def deny(self, action_id: str) -> None:
        self._denylist.add(action_id)

    def set_allowlist(self, actions: list[str]) -> None:
        self._allowlist = set(actions)

    def reason(self, action_id: str, now: float | None = None) -> str | None:
        """Returns the blocking reason, or None when the call is allowed."""
        anchor = now if now is not None else time.time()
        if action_id in self._denylist:
            return f"action denied: {action_id}"
        if self._allowlist and action_id not in self._allowlist:
            return f"action not in allowlist: {action_id}"
        last = self._last.get(action_id)
        if last is not None and self.cooldown > 0 and anchor - last < self.cooldown:
            return f"action on cooldown ({self.cooldown}s)"
        calls = [t for t in self._calls.get(action_id, [])
                 if anchor - t < self.window]
        if len(calls) >= self.max_calls:
            return "rate limit exceeded"
        return None

    def record_call(self, action_id: str, now: float | None = None) -> None:
        anchor = now if now is not None else time.time()
        self._calls.setdefault(action_id, []).append(anchor)
        self._last[action_id] = anchor

    def remaining(self, action_id: str, now: float | None = None) -> int:
        anchor = now if now is not None else time.time()
        calls = [t for t in self._calls.get(action_id, [])
                 if anchor - t < self.window]
        return max(0, self.max_calls - len(calls))

    def reset(self) -> None:
        self._calls.clear()
        self._last.clear()
