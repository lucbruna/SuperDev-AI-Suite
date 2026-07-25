"""Plugin registry for CLI extensions."""


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, dict] = {}

    def register(self, name: str, version: str, description: str = "", commands: list[str] | None = None) -> None:
        self._plugins[name] = {
            "version": version,
            "description": description,
            "commands": commands or [],
        }

    def get(self, name: str) -> dict | None:
        return self._plugins.get(name)

    def list(self) -> list[dict]:
        return [{"name": k, **v} for k, v in self._plugins.items()]

    def has(self, name: str) -> bool:
        return name in self._plugins

    def commands(self) -> dict[str, str]:
        result = {}
        for plugin in self._plugins.values():
            for cmd in plugin["commands"]:
                result[cmd] = plugin.get("description", "")
        return result
