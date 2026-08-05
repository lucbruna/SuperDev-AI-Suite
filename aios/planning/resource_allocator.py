"""ResourceAllocator: tracks capacity and assignment for named resources."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.planning.task_builder import Task


@dataclass
class Resource:
    name: str
    capacity: int = 1
    kind: str = "generic"
    allocated: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def available(self) -> int:
        return max(0, self.capacity - self.allocated)


class ResourceAllocator:
    """In-memory capacity tracker. Allocation never exceeds capacity."""

    def __init__(self) -> None:
        self._resources: dict[str, Resource] = {}

    def register(self, name: str, capacity: int = 1, kind: str = "generic", **metadata: Any) -> Resource:
        if name in self._resources:
            raise KeyError(f"resource {name!r} already registered")
        capacity = max(0, int(capacity))
        resource = Resource(name=name, capacity=capacity, kind=kind, metadata=dict(metadata))
        self._resources[name] = resource
        return resource

    def get(self, name: str) -> Resource | None:
        return self._resources.get(name)

    def resources(self) -> list[Resource]:
        return [self._resources[name] for name in sorted(self._resources)]

    def availability(self, name: str) -> int:
        resource = self.get(name)
        return resource.available if resource is not None else 0

    def can_allocate(self, name: str, amount: int = 1) -> bool:
        return self.availability(name) >= max(1, int(amount))

    def allocate(self, name: str, amount: int = 1) -> bool:
        amount = max(1, int(amount))
        if not self.can_allocate(name, amount):
            return False
        self._resources[name].allocated += amount
        return True

    def release(self, name: str, amount: int = 1) -> bool:
        resource = self.get(name)
        if resource is None:
            return False
        resource.allocated = max(0, resource.allocated - max(1, int(amount)))
        return True

    def assign(self, task: Task, name: str, amount: int = 1) -> bool:
        if self.allocate(name, amount):
            task.resource = name
            return True
        return False

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "capacity": r.capacity,
                "kind": r.kind,
                "allocated": r.allocated,
                "available": r.available,
            }
            for name, r in sorted(self._resources.items())
        }
