"""Route table: endpoint name -> required permission."""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.api.digital_twin_endpoints import (
    ENDPOINT_ANALYZE,
    ENDPOINT_BUILD_TWIN,
    ENDPOINT_CONFIG,
    ENDPOINT_CYCLE,
    ENDPOINT_ENDPOINTS,
    ENDPOINT_REGISTER_COMPONENT,
    ENDPOINT_SNAPSHOT,
    ENDPOINT_START,
    ENDPOINT_STATUS,
    ENDPOINT_STOP,
    ENDPOINT_TICK,
    ENDPOINT_VALIDATE,
)
from modules.digital_twin.config.constants import (
    PERM_MANAGE_TWIN,
    PERM_RUN_PREDICTION,
    PERM_RUN_SIMULATION,
    PERM_TRIGGER_SYNC,
    PERM_VIEW_TWIN,
)


@dataclass(frozen=True, slots=True)
class Route:
    """A named endpoint plus its required permission."""

    name: str
    permission: str


ROUTES: tuple[Route, ...] = (
    Route(ENDPOINT_STATUS, PERM_VIEW_TWIN),
    Route(ENDPOINT_ENDPOINTS, PERM_VIEW_TWIN),
    Route(ENDPOINT_CONFIG, PERM_VIEW_TWIN),
    Route(ENDPOINT_START, PERM_MANAGE_TWIN),
    Route(ENDPOINT_STOP, PERM_MANAGE_TWIN),
    Route(ENDPOINT_CYCLE, PERM_TRIGGER_SYNC),
    Route(ENDPOINT_TICK, PERM_TRIGGER_SYNC),
    Route(ENDPOINT_REGISTER_COMPONENT, PERM_MANAGE_TWIN),
    Route(ENDPOINT_BUILD_TWIN, PERM_RUN_SIMULATION),
    Route(ENDPOINT_SNAPSHOT, PERM_VIEW_TWIN),
    Route(ENDPOINT_ANALYZE, PERM_VIEW_TWIN),
    Route(ENDPOINT_VALIDATE, PERM_VIEW_TWIN),
)

ROUTE_BY_NAME: dict[str, Route] = {route.name: route for route in ROUTES}


def permission_for(endpoint: str) -> str:
    route = ROUTE_BY_NAME.get(endpoint)
    return route.permission if route else PERM_VIEW_TWIN
