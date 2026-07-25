from typing import Any, Dict


class CLIApplication:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.registry: Dict[str, Any] = {}

    def register(self, key: str, value: Any) -> None:
        self.registry[key] = value

    def get(self, key: str) -> Any:
        return self.registry.get(key)

    def run(self) -> None:
        from cli.main import cli
        cli()