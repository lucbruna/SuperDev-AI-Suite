"""Plugin loader for CLI extensions."""

import importlib
import sys
from pathlib import Path


class PluginLoader:
    def __init__(self, plugin_dir: str = "~/.superdev/plugins"):
        self.plugin_dir = Path(plugin_dir).expanduser()
        self.plugins: dict[str, any] = {}

    def discover(self) -> list[str]:
        if not self.plugin_dir.exists():
            return []
        return [p.name for p in self.plugin_dir.iterdir() if p.is_dir() and (p / "__init__.py").exists()]

    def load(self, name: str) -> any:
        if name in self.plugins:
            return self.plugins[name]

        plugin_path = self.plugin_dir / name
        if not plugin_path.exists():
            raise ImportError(f"Plugin not found: {name}")

        sys.path.insert(0, str(self.plugin_dir))
        try:
            module = importlib.import_module(name)
            self.plugins[name] = module
            return module
        finally:
            sys.path.pop(0)

    def load_all(self) -> dict[str, any]:
        for name in self.discover():
            try:
                self.load(name)
            except Exception as e:
                print(f"Failed to load plugin {name}: {e}")
        return self.plugins
