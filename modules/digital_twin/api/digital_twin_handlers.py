"""Handlers: route names mapped to controller calls."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from modules.digital_twin.api.digital_twin_controllers import TwinControllers
from modules.digital_twin.api.digital_twin_responses import ApiResponse

HandlerFn = Callable[..., ApiResponse]


@dataclass(slots=True)
class TwinHandlers:
    """Binds route names to controller operations."""

    controllers: TwinControllers

    def handlers(self) -> dict[str, HandlerFn]:
        return {
            "status": self.controllers.status,
            "config": self.controllers.config,
            "start": self.controllers.start,
            "stop": self.controllers.stop,
            "cycle": self.controllers.cycle,
            "tick": self.controllers.tick,
            "register_component": self.controllers.register_component,
            "build_twin": self.controllers.build_twin,
            "snapshot": self.controllers.snapshot,
            "analyze": self.controllers.analyze,
            "validate": self.controllers.validate,
        }
