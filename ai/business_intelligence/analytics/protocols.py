"""Analytics protocols."""
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: Dict[str, Any]): ...


@runtime_checkable
class Cacheable(Protocol):
    def cache_key(self) -> str: ...
    def cache_ttl(self) -> int: ...


@runtime_checkable
class Validatable(Protocol):
    def validate(self) -> bool: ...
    def errors(self) -> list: ...
