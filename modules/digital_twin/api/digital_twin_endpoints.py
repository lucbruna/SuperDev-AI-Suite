"""Endpoint names for the Digital Twin API."""
from __future__ import annotations

# Runtime introspection.
ENDPOINT_STATUS = "status"
ENDPOINT_ENDPOINTS = "endpoints"
ENDPOINT_CONFIG = "config"

# Lifecycle control.
ENDPOINT_START = "start"
ENDPOINT_STOP = "stop"
ENDPOINT_CYCLE = "cycle"
ENDPOINT_TICK = "tick"
ENDPOINT_REGISTER_COMPONENT = "register_component"

# Twin operations.
ENDPOINT_BUILD_TWIN = "build_twin"
ENDPOINT_SNAPSHOT = "snapshot"
ENDPOINT_ANALYZE = "analyze"
ENDPOINT_VALIDATE = "validate"

ALL_ENDPOINTS: tuple[str, ...] = (
    ENDPOINT_STATUS,
    ENDPOINT_ENDPOINTS,
    ENDPOINT_CONFIG,
    ENDPOINT_START,
    ENDPOINT_STOP,
    ENDPOINT_CYCLE,
    ENDPOINT_TICK,
    ENDPOINT_REGISTER_COMPONENT,
    ENDPOINT_BUILD_TWIN,
    ENDPOINT_SNAPSHOT,
    ENDPOINT_ANALYZE,
    ENDPOINT_VALIDATE,
)
