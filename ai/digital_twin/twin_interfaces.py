"""Digital Twin interfaces."""
from __future__ import annotations
from typing import Any, Dict, Protocol, runtime_checkable

@runtime_checkable
class Simulatable(Protocol):
    def simulate(self, config: Dict[str, Any]) -> Dict[str, Any]: ...

@runtime_checkable
class Predictable(Protocol):
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]: ...

@runtime_checkable
class Optimizable(Protocol):
    def optimize(self, objective: str, constraints: Dict[str, Any]) -> Dict[str, Any]: ...

@runtime_checkable
class Syncable(Protocol):
    def sync(self, data: Dict[str, Any]) -> Dict[str, Any]: ...

@runtime_checkable
class Visualizable(Protocol):
    def visualize(self, config: Dict[str, Any]) -> Dict[str, Any]: ...

@runtime_checkable
class Validatable(Protocol):
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]: ...
