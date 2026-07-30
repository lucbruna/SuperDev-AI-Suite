from __future__ import annotations

from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class Executable(Protocol):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]: ...


@runtime_checkable
class Routable(Protocol):
    def route(self, task: Dict[str, Any]) -> str: ...


@runtime_checkable
class Recoverable(Protocol):
    def recover(self) -> bool: ...


@runtime_checkable
class Storable(Protocol):
    def save(self) -> bool: ...
    def load(self) -> bool: ...


@runtime_checkable
class Monitorable(Protocol):
    def heartbeat(self) -> None: ...
    def status(self) -> str: ...
