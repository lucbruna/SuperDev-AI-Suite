"""Digital Twin API facade."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.api.digital_twin_controllers import TwinControllers
from modules.digital_twin.api.digital_twin_dependencies import TwinDependencies
from modules.digital_twin.api.digital_twin_handlers import TwinHandlers
from modules.digital_twin.api.digital_twin_middleware import (
    MiddlewareChain,
    audit_middleware,
)
from modules.digital_twin.api.digital_twin_responses import ApiResponse
from modules.digital_twin.api.digital_twin_router import TwinRouter
from modules.digital_twin.config.permissions import Permissions
from modules.digital_twin.core.digital_twin_manager import DigitalTwinManager
from modules.digital_twin.twin_engine.digital_twin_analyzer import TwinAnalyzer
from modules.digital_twin.twin_engine.digital_twin_engine import TwinEngine
from modules.digital_twin.twin_engine.digital_twin_registry import TwinModelRegistry
from modules.digital_twin.twin_engine.digital_twin_validator import TwinValidator


@dataclass(slots=True)
class DigitalTwinAPI:
    """Top-level API object wiring dependencies, controllers and router."""

    manager: DigitalTwinManager
    permissions: Permissions | None = None
    audit_log: list[dict[str, object]] | None = None
    twin_engine: TwinEngine | None = None
    twin_registry: TwinModelRegistry | None = None
    _router: TwinRouter = field(init=False, repr=False)
    _deps: TwinDependencies = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._deps = TwinDependencies(
            manager=self.manager,
            config=self.manager.context.config,
            permissions=self.permissions,
            audit_log=self.audit_log,
        )
        controllers = TwinControllers(
            manager=self.manager,
            twin_engine=self.twin_engine,
            validator=TwinValidator(),
            analyzer=TwinAnalyzer(),
            twin_registry=self.twin_registry,
        )
        handlers = TwinHandlers(controllers).handlers()
        router = TwinRouter(handlers=handlers, permissions=self.permissions)
        if self.audit_log is not None:
            router.middleware.add(audit_middleware(self.audit_log))
        self._router = router

    @property
    def router(self) -> TwinRouter:
        return self._router

    def dispatch(
        self,
        endpoint: str,
        params: dict[str, object] | None = None,
        *,
        role: str = "admin",
    ) -> ApiResponse:
        return self._router.dispatch(endpoint, params, role=role)

    def endpoints(self) -> list[str]:
        return self._router.endpoint_names()
