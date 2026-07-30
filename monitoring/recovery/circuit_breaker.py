from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Callable


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern to prevent repeated failures."""

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3,
    ) -> None:
        self._name = name
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0
        self._on_state_change: list[Callable[[CircuitState], None]] = []
        self._logger = logging.getLogger(f"superdev.recovery.circuit.{name}")

    @property
    def state(self) -> CircuitState:
        return self._state

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if not self._allow_request():
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self._name}' is {self._state.value}"
            )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _allow_request(self) -> bool:
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self._recovery_timeout:
                self._set_state(CircuitState.HALF_OPEN)
                return True
            return False

        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_calls < self._half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False

        return False

    def _on_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._failure_count = 0
            self._half_open_calls = 0
            self._set_state(CircuitState.CLOSED)
        else:
            self._failure_count = 0

    def _on_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._set_state(CircuitState.OPEN)
        elif self._failure_count >= self._failure_threshold:
            self._set_state(CircuitState.OPEN)

    def _set_state(self, new_state: CircuitState) -> None:
        if self._state == new_state:
            return
        old = self._state
        self._state = new_state
        self._logger.info("State change: %s -> %s", old.value, new_state.value)
        for cb in self._on_state_change:
            try:
                cb(new_state)
            except Exception:
                pass

    def on_state_change(self, callback: Callable[[CircuitState], None]) -> None:
        self._on_state_change.append(callback)

    def reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0


class CircuitBreakerOpenError(Exception):
    """Raised when a circuit breaker is open and rejects a request."""
    pass
