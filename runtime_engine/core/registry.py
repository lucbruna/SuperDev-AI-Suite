from typing import TypeVar, Generic
from runtime_engine.runtime.runtime import BaseRuntime


R = TypeVar("R", bound=BaseRuntime)


class RuntimeRegistry:
    def __init__(self) -> None:
        self._runtimes: dict[str, type[BaseRuntime]] = {}

    def register(self, language: str, runtime_class: type[BaseRuntime]) -> None:
        self._runtimes[language.lower()] = runtime_class

    def get(self, language: str) -> type[BaseRuntime] | None:
        return self._runtimes.get(language.lower())

    def list(self) -> list[str]:
        return list(self._runtimes.keys())

    def has(self, language: str) -> bool:
        return language.lower() in self._runtimes

    def __len__(self) -> int:
        return len(self._runtimes)
