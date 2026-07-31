from __future__ import annotations

import logging
from typing import Any, Callable


class FrontendFactory:
    """Factory for creating frontend subsystems and screens."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.factory")
        self._factories: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, factory: Callable[..., Any]) -> None:
        self._factories[name] = factory

    def create(self, name: str, **kwargs: Any) -> Any:
        if name not in self._factories:
            raise KeyError(f"no factory registered for: {name}")
        return self._factories[name](**kwargs)

    def available(self) -> list[str]:
        return list(self._factories)
