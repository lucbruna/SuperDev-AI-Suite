from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


class ModuleLoader:
    def __init__(self) -> None:
        self._modules: dict[str, ModuleType] = {}

    def import_module(self, path: str | Path) -> ModuleType:
        module_path = Path(path).resolve()
        if not module_path.exists():
            raise FileNotFoundError(f"Module not found: {module_path}")

        module_name = module_path.stem
        if module_name in sys.modules:
            return sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, str(module_path))
        if spec is None:
            raise ImportError(f"Could not load spec from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        if spec.loader:
            spec.loader.exec_module(module)

        self._modules[module_name] = module
        return module

    def get_module(self, name: str) -> ModuleType | None:
        return self._modules.get(name) or sys.modules.get(name)

    def reload_module(self, name: str) -> ModuleType:
        if name in sys.modules:
            module = importlib.reload(sys.modules[name])
            self._modules[name] = module
            return module
        raise ImportError(f"Module '{name}' is not loaded")
