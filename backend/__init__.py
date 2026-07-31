"""Backend package.

Usa lazy imports para evitar que importar qualquer submodulo
dispare a carga de app e config (que tem dependencias pesadas).
"""

import importlib
from typing import Any


def __getattr__(name: str) -> Any:
    if name == "create_app":
        mod = importlib.import_module("backend.app")
        return mod.create_app
    if name == "settings":
        mod = importlib.import_module("backend.config")
        return mod.settings
    if name == "config":
        mod = importlib.import_module("backend.config")
        return mod.config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["create_app", "settings", "config"]
