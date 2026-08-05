"""Module: unit of extensibility in the AIOS module system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class Module:
    module_id: str
    name: str
    version: str = "1.0.0"
    entrypoint: Optional[Callable[[], Any]] = None
    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    status: str = "registered"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "version": self.version,
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "status": self.status,
            "metadata": dict(self.metadata),
        }
