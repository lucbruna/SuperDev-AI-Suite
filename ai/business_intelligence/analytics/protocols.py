"""Analytics protocols."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]): ...


@runtime_checkable
class Cacheable(Protocol):
    def cache_key(self) -> str: ...
    def cache_ttl(self) -> int: ...


@runtime_checkable
class Validatable(Protocol):
    def validate(self) -> bool: ...
    def errors(self) -> list: ...
