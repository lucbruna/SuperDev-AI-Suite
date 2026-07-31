"""DevOps interfaces."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Provisionable(Protocol):
    def provision(self, config: dict[str, Any]) -> dict[str, Any]: ...
    def deprovision(self, resource_id: str) -> bool: ...


@runtime_checkable
class Deployable(Protocol):
    def deploy(self, config: dict[str, Any]) -> dict[str, Any]: ...
    def rollback(self, deployment_id: str) -> bool: ...


@runtime_checkable
class Scalable(Protocol):
    def scale_up(self, amount: int) -> dict[str, Any]: ...
    def scale_down(self, amount: int) -> dict[str, Any]: ...


@runtime_checkable
class Monitorable(Protocol):
    def get_status(self) -> dict[str, Any]: ...
    def get_metrics(self) -> dict[str, Any]: ...
