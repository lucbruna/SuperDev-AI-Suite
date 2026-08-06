"""Component registry for the Digital Twin module.

Always construct a fresh registry per runtime/tests — never rely on a shared
singleton, mirroring the Autonomous Developer module's registry pattern.
"""
from __future__ import annotations

from collections.abc import Callable

Component = Callable[..., object]


class TwinRegistryError(KeyError):
    """Raised on registry misuse."""


class TwinRegistry:
    """Named component registry with simple lifecycle helpers.

    Plain class (no dataclass slots): the backing dict is created in
    ``__init__``.
    """

    def __init__(self) -> None:
        self._components: dict[str, Component] = {}

    def register(self, name: str, component: Component, *, overwrite: bool = False) -> None:
        if name in self._components and not overwrite:
            raise TwinRegistryError(f"component already registered: {name}")
        self._components[name] = component

    def get(self, name: str) -> Component:
        try:
            return self._components[name]
        except KeyError:
            raise TwinRegistryError(f"component not found: {name}") from None

    def has(self, name: str) -> bool:
        return name in self._components

    def names(self) -> list[str]:
        return sorted(self._components)

    def all(self) -> dict[str, Component]:
        return dict(self._components)

    def unregister(self, name: str) -> None:
        self._components.pop(name, None)

    def clear(self) -> None:
        self._components.clear()

    def __len__(self) -> int:
        return len(self._components)
