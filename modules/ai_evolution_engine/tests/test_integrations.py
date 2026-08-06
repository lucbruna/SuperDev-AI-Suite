"""Unit tests: integrations package (graceful degradation)."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations import build_default_registry
from modules.ai_evolution_engine.integrations.integration_registry import (
    IntegrationRegistry,
    ModuleConnector,
)
from modules.ai_evolution_engine.tests.helpers import make_context


def test_registry_registers_and_lists():
    registry = IntegrationRegistry()
    registry.register(ModuleConnector(name="sibling", description="d"))
    assert registry.names() == ["sibling"]
    assert registry.available("sibling") is False
    assert registry.available("missing") is False


def test_module_connector_degrades_when_module_missing():
    connector = ModuleConnector(
        name="missing_module", description="d", module="modules.does_not_exist"
    )
    ctx = make_context()
    payload = connector.collect(ctx)
    assert payload == {"available": False, "name": "missing_module"}


def test_module_connector_detects_real_sibling():
    connector = ModuleConnector(
        name="self_healing",
        description="d",
        module="modules.self_healing_engine",
        public_api=("HealingEngine",),
    )
    ctx = make_context()
    payload = connector.collect(ctx)
    assert payload["available"] is True
    assert payload["name"] == "self_healing"


def test_default_registry_summary_is_deterministic():
    registry = build_default_registry()
    summary = registry.summary()
    assert isinstance(summary, dict)
    assert "self_healing" in summary
    assert summary["self_healing"] is True
    # running twice yields identical output
    assert registry.summary() == summary


def test_collect_all_never_raises():
    registry = build_default_registry()
    payload = registry.collect_all(make_context())
    assert set(payload) == set(registry.names())
    for name, data in payload.items():
        assert "available" in data
