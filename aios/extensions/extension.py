"""Extension: base class and context for the AIOS extension system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

#: hook function signature: (*args, **kwargs) -> Any
HookFunc = Callable[..., Any]

HOOK_POINTS = (
    "before_run",
    "after_run",
    "before_node",
    "after_node",
    "on_event",
    "on_error",
)


@dataclass
class ExtensionContext:
    """Shared services made available to extensions at registration time."""

    event_bus: Any = None
    memory: Any = None
    logger: Any = None
    config: dict[str, Any] = field(default_factory=dict)


class Extension:
    """Base class; subclasses override ``hooks()`` and lifecycle callbacks."""

    name: str = ""
    version: str = "1.0.0"

    def __init__(self, context: Optional[ExtensionContext] = None) -> None:
        self.context = context if context is not None else ExtensionContext()
        self.enabled: bool = True

    def hooks(self) -> dict[str, HookFunc]:
        """Map hook point -> handler. Called once at registration."""
        return {}

    def on_load(self) -> None:
        """Lifecycle callback when the extension is registered/loaded."""

    def on_unload(self) -> None:
        """Lifecycle callback when the extension is removed."""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "version": self.version, "enabled": self.enabled}
