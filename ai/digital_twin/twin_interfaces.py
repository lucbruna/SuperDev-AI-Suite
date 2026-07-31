"""Digital Twin interfaces."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Simulatable(Protocol):
    def simulate(self, config: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class Predictable(Protocol):
    def predict(self, data: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class Optimizable(Protocol):
    def optimize(self, objective: str, constraints: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class Syncable(Protocol):
    def sync(self, data: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class Visualizable(Protocol):
    def visualize(self, config: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class Validatable(Protocol):
    def validate(self, data: dict[str, Any]) -> dict[str, Any]: ...
