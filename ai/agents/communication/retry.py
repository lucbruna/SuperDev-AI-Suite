from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class Retry:
    """Retry mechanism for message delivery."""

    def __init__(self, max_retries: int = 3, delay: float = 1.0) -> None:
        self._max_retries = max_retries
        self._delay = delay
        self._attempts: int = 0

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def attempts(self) -> int:
        return self._attempts

    def execute(self, func: Callable[[], Any]) -> Optional[Any]:
        self._attempts = 0
        last_error: Optional[Exception] = None
        while self._attempts < self._max_retries:
            try:
                self._attempts += 1
                return func()
            except Exception as e:
                last_error = e
        if last_error:
            raise last_error
        return None

    def reset(self) -> None:
        self._attempts = 0
