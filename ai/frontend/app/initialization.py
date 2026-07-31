"""
Frontend Application Initialization
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class InitPhase(Enum):
    """Initialization phases."""

    PENDING = "pending"
    CONFIG = "config"
    SERVICES = "services"
    AUTH = "auth"
    THEME = "theme"
    I18N = "i18n"
    ROUTES = "routes"
    PLUGINS = "plugins"
    WEBSOCKET = "websocket"
    READY = "ready"
    ERROR = "error"


@dataclass
class InitStep:
    """Initialization step."""

    name: str
    phase: InitPhase
    callback: Any
    required: bool = True
    dependencies: list[str] = field(default_factory=list)
    completed: bool = False
    error: str | None = None


class AppInitializer:
    """Application initialization manager."""

    def __init__(self):
        self.phase = InitPhase.PENDING
        self.steps: list[InitStep] = []
        self.errors: list[str] = []
        self.listeners: list[Any] = []
        self.config: dict[str, Any] = {}

    def add_step(
        self, name: str, phase: InitPhase, callback: Any, required: bool = True, dependencies: list[str] | None = None
    ) -> None:
        """Add an initialization step."""
        step = InitStep(name=name, phase=phase, callback=callback, required=required, dependencies=dependencies or [])
        self.steps.append(step)

    def remove_step(self, name: str) -> None:
        """Remove an initialization step."""
        self.steps = [s for s in self.steps if s.name != name]

    def get_step(self, name: str) -> InitStep | None:
        """Get a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def set_config(self, config: dict[str, Any]) -> None:
        """Set initialization configuration."""
        self.config = config

    async def initialize(self) -> bool:
        """Run initialization sequence."""
        self.phase = InitPhase.CONFIG
        self._notify("start", {"phase": self.phase})

        try:
            # Group steps by phase
            phases = [
                InitPhase.CONFIG,
                InitPhase.SERVICES,
                InitPhase.AUTH,
                InitPhase.THEME,
                InitPhase.I18N,
                InitPhase.ROUTES,
                InitPhase.PLUGINS,
                InitPhase.WEBSOCKET,
            ]

            for phase in phases:
                self.phase = phase
                self._notify("phase", {"phase": phase})

                phase_steps = [s for s in self.steps if s.phase == phase]

                for step in phase_steps:
                    if step.completed:
                        continue

                    # Check dependencies
                    deps_met = all(self._is_step_completed(dep) for dep in step.dependencies)

                    if not deps_met:
                        if step.required:
                            raise Exception(f"Dependencies not met for required step: {step.name}")
                        continue

                    try:
                        if step.callback:
                            result = step.callback(self.config)
                            if hasattr(result, "__await__"):
                                await result
                        step.completed = True
                        self._notify("step_complete", {"step": step.name})
                    except Exception as e:
                        step.error = str(e)
                        self.errors.append(f"{step.name}: {str(e)}")
                        self._notify("step_error", {"step": step.name, "error": str(e)})

                        if step.required:
                            raise

            self.phase = InitPhase.READY
            self._notify("complete", {"phase": self.phase})
            return True

        except Exception as e:
            self.phase = InitPhase.ERROR
            self.errors.append(str(e))
            self._notify("error", {"error": str(e)})
            return False

    def _is_step_completed(self, step_name: str) -> bool:
        """Check if a step is completed."""
        step = self.get_step(step_name)
        return step is not None and step.completed

    def on(self, event: str, callback: Any) -> None:
        """Register event listener."""
        self.listeners.append({"event": event, "callback": callback})

    def _notify(self, event: str, data: dict[str, Any]) -> None:
        """Notify listeners."""
        for listener in self.listeners:
            if listener["event"] == event:
                listener["callback"](data)

    def get_status(self) -> dict[str, Any]:
        """Get initialization status."""
        return {
            "phase": self.phase.value,
            "steps": [
                {"name": s.name, "phase": s.phase.value, "completed": s.completed, "error": s.error} for s in self.steps
            ],
            "errors": self.errors,
            "is_ready": self.phase == InitPhase.READY,
        }

    def reset(self) -> None:
        """Reset initialization state."""
        self.phase = InitPhase.PENDING
        for step in self.steps:
            step.completed = False
            step.error = None
        self.errors.clear()


def create_default_initializer(config: dict[str, Any] | None = None) -> AppInitializer:
    """Create a default application initializer."""
    initializer = AppInitializer()

    if config:
        initializer.set_config(config)

    # Add default initialization steps
    def init_config(cfg: dict[str, Any]) -> None:
        """Initialize configuration."""
        pass

    def init_services(cfg: dict[str, Any]) -> None:
        """Initialize core services."""
        pass

    def init_auth(cfg: dict[str, Any]) -> None:
        """Initialize authentication."""
        pass

    def init_theme(cfg: dict[str, Any]) -> None:
        """Initialize theme."""
        pass

    def init_i18n(cfg: dict[str, Any]) -> None:
        """Initialize internationalization."""
        pass

    def init_routes(cfg: dict[str, Any]) -> None:
        """Initialize routes."""
        pass

    def init_plugins(cfg: dict[str, Any]) -> None:
        """Initialize plugins."""
        pass

    def init_websocket(cfg: dict[str, Any]) -> None:
        """Initialize WebSocket."""
        pass

    initializer.add_step("config", InitPhase.CONFIG, init_config, required=True)
    initializer.add_step("services", InitPhase.SERVICES, init_services, required=True, dependencies=["config"])
    initializer.add_step("auth", InitPhase.AUTH, init_auth, required=False, dependencies=["services"])
    initializer.add_step("theme", InitPhase.THEME, init_theme, required=False, dependencies=["config"])
    initializer.add_step("i18n", InitPhase.I18N, init_i18n, required=False, dependencies=["config"])
    initializer.add_step("routes", InitPhase.ROUTES, init_routes, required=True, dependencies=["auth"])
    initializer.add_step("plugins", InitPhase.PLUGINS, init_plugins, required=False, dependencies=["services"])
    initializer.add_step("websocket", InitPhase.WEBSOCKET, init_websocket, required=False, dependencies=["services"])

    return initializer
