"""RetryPolicy: deterministic retry decisions and backoff delays."""
from __future__ import annotations

from typing import Any, Type

BACKOFFS = ("fixed", "linear", "exponential")


class RetryPolicy:
    """Decides whether an attempt should be retried and the delay before it.

    An attempt is retryable when it is below ``max_attempts`` and the raised
    error is an instance of one of the ``retryable`` exception types.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        backoff: str = "exponential",
        base_delay: float = 0.1,
        max_delay: float = 5.0,
        retryable: tuple[Type[BaseException], ...] | None = None,
    ) -> None:
        if backoff not in BACKOFFS:
            raise ValueError(f"unknown backoff {backoff!r}; expected one of {BACKOFFS}")
        self.max_attempts = max(1, int(max_attempts))
        self.backoff = backoff
        self.base_delay = max(0.0, float(base_delay))
        self.max_delay = max(0.0, float(max_delay))
        self.retryable = tuple(retryable) if retryable else (Exception,)

    def should_retry(self, attempts: int, error: BaseException | None = None) -> bool:
        if attempts >= self.max_attempts:
            return False
        if error is not None and not isinstance(error, self.retryable):
            return False
        return True

    def next_delay(self, attempts: int) -> float:
        a = max(1, int(attempts))
        if self.backoff == "fixed":
            delay = self.base_delay
        elif self.backoff == "linear":
            delay = self.base_delay * a
        else:
            delay = self.base_delay * (2 ** (a - 1))
        return round(min(delay, self.max_delay), 6)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_attempts": self.max_attempts,
            "backoff": self.backoff,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "retryable": [cls.__name__ for cls in self.retryable],
        }
