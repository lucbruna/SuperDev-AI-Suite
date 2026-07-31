from __future__ import annotations

import pytest

from frontend import FrontendEngine
from frontend.frontend_events import FrontendEvents
from frontend.frontend_metrics import FrontendMetrics
from frontend.frontend_registry import FrontendRegistry
from frontend.frontend_security import FrontendSecurity


def test_engine_initializes() -> None:
    engine = FrontendEngine()
    engine.initialize()
    assert engine.status()["initialized"] is True


def test_events_publish_subscribe() -> None:
    events = FrontendEvents()
    received: list[tuple[str, dict]] = []

    def listener(event_type: str, payload: dict) -> None:
        received.append((event_type, payload))

    events.on("test", listener)
    events.emit("test", {"value": "hello"})

    assert received == [("test", {"value": "hello"})]


def test_metrics_record_and_get() -> None:
    metrics = FrontendMetrics()
    for value in (10, 20, 30):
        metrics.record("requests", value)
    snapshot = metrics.snapshot()
    assert "requests" in snapshot
    assert metrics.get("requests") is not None


def test_registry_prefix_matching() -> None:
    registry = FrontendRegistry()
    registry.register_route("/api/agents", "agents")
    registry.register_route("/api/projects", "projects")
    resolved = registry.resolve_route("/api/projects/123")
    assert resolved is not None
    assert resolved["handler"] == "projects"


def test_security_token_flow() -> None:
    security = FrontendSecurity()
    token = security.issue_token("user-1", ttl=60)
    payload = security.validate_token(token)
    assert payload is not None
    assert payload.get("user") == "user-1"


def test_security_denies_unknown_token() -> None:
    security = FrontendSecurity()
    with pytest.raises(ValueError):
        security.validate_token("bogus-token")
