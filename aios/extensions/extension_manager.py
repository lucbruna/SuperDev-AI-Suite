"""ExtensionManager: lifecycle and hook gating for registered extensions."""
from __future__ import annotations

from typing import Any, Optional

from aios.extensions.extension import Extension, ExtensionContext, HOOK_POINTS
from aios.extensions.hook_registry import FireResult, HookRegistry


class ExtensionManager:
    """Facade: register/enable/disable extensions and fire their hooks."""

    def __init__(self, hooks: HookRegistry | None = None) -> None:
        self.hooks = hooks if hooks is not None else HookRegistry()
        self._extensions: dict[str, Extension] = {}

    def register(self, extension: Extension) -> bool:
        if extension.name in self._extensions:
            raise KeyError(f"extension {extension.name!r} already registered")
        self._extensions[extension.name] = extension
        extension.on_load()
        for hook_point, handler in extension.hooks().items():
            self.hooks.register(extension.name, hook_point, handler)
        return True

    def unregister(self, name: str) -> bool:
        extension = self._extensions.pop(name, None)
        if extension is None:
            return False
        extension.on_unload()
        self.hooks.remove_extension(name)
        return True

    def enable(self, name: str) -> bool:
        extension = self._extensions.get(name)
        if extension is None:
            return False
        extension.enabled = True
        return True

    def disable(self, name: str) -> bool:
        extension = self._extensions.get(name)
        if extension is None:
            return False
        extension.enabled = False
        return True

    def status(self, name: str) -> Optional[str]:
        extension = self._extensions.get(name)
        return "enabled" if extension is not None and extension.enabled else (
            "disabled" if extension is not None else None
        )

    def extensions(self) -> list[str]:
        return sorted(self._extensions)

    def enabled_extensions(self) -> list[str]:
        return sorted(name for name, ext in self._extensions.items() if ext.enabled)

    def get(self, name: str) -> Optional[Extension]:
        return self._extensions.get(name)

    def fire(self, hook_point: str, *args: Any, **kwargs: Any) -> FireResult:
        return self.hooks.fire(
            hook_point,
            enabled=lambda name: name in self._extensions and self._extensions[name].enabled,
            *args,
            **kwargs,
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "total": len(self._extensions),
            "enabled": len(self.enabled_extensions()),
            "extensions": [self._extensions[name].to_dict() for name in self.extensions()],
            "hooks": self.hooks.snapshot(),
        }


def make_extension_manager(
    extensions: list[Extension], context: ExtensionContext | None = None
) -> ExtensionManager:
    """Convenience factory: register a list of extensions in order."""
    manager = ExtensionManager()
    for extension in extensions:
        if context is not None:
            extension.context = context
        manager.register(extension)
    return manager
