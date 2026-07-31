"""AI Model protocols."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Inferable(Protocol):
    def infer(self, prompt: str, **kwargs: Any) -> dict[str, Any]: ...

@runtime_checkable
class Evaluable(Protocol):
    def evaluate(self, test_cases: list) -> dict[str, float]: ...

@runtime_checkable
class Cacheable(Protocol):
    def get_cached(self, key: str) -> Any: ...
    def set_cached(self, key: str, value: Any) -> bool: ...

@runtime_checkable
class CostTrackable(Protocol):
    def get_cost(self) -> float: ...
    def is_within_budget(self) -> bool: ...

@runtime_checkable
class Securable(Protocol):
    def validate_input(self, data: Any) -> bool: ...
    def sanitize_output(self, data: Any) -> Any: ...
