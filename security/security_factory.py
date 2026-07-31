"""Factory for the Security Engine subsystems (Volume 16)."""

from __future__ import annotations

from typing import Any


class SecurityFactory:
    """Instantiates security subsystems, wiring shared dependencies."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def create(self, name: str, cls: type, **kwargs: Any) -> Any:
        """Create a subsystem instance wired with the engine by default."""
        instance = cls(engine=self.engine, **kwargs)
        self.engine.registry.register_artifact(name, instance)
        return instance

    def build_all(self) -> dict[str, Any]:
        """Build every subsystem via the engine's lazy wiring."""
        return self.engine.subsystems()
