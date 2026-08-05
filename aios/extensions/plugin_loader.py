"""PluginLoader: factory-based loading of extensions."""
from __future__ import annotations

from typing import Any, Callable, Optional

from aios.extensions.extension import Extension, ExtensionContext

#: factory: (context) -> Extension
ExtensionFactory = Callable[[ExtensionContext], Extension]


class PluginLoader:
    """Instantiates extensions from registered factories with a shared context."""

    def __init__(self) -> None:
        self._factories: dict[str, ExtensionFactory] = {}
        self._loaded: dict[str, Extension] = {}

    def register_factory(self, name: str, factory: ExtensionFactory) -> bool:
        if name in self._factories:
            raise KeyError(f"factory {name!r} already registered")
        self._factories[name] = factory
        return True

    def load(self, name: str, context: Optional[ExtensionContext] = None) -> Extension:
        factory = self._factories.get(name)
        if factory is None:
            raise KeyError(f"no factory registered for extension {name!r}")
        if name in self._loaded:
            return self._loaded[name]
        extension = factory(context if context is not None else ExtensionContext())
        self._loaded[name] = extension
        return extension

    def load_all(self, names: list[str], context: Optional[ExtensionContext] = None) -> list[Extension]:
        return [self.load(name, context) for name in names]

    def unload(self, name: str) -> bool:
        extension = self._loaded.pop(name, None)
        if extension is None:
            return False
        extension.on_unload()
        return True

    def loaded(self) -> list[str]:
        return sorted(self._loaded)

    def snapshot(self) -> dict[str, Any]:
        return {
            "factories": sorted(self._factories),
            "loaded": self.loaded(),
            "extensions": [self._loaded[name].to_dict() for name in self.loaded()],
        }
