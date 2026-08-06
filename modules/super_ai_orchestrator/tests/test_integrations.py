"""Unit tests: integrations (connectors, graceful degradation)."""
from __future__ import annotations

from modules.super_ai_orchestrator.integrations import ConnectorRegistry
from modules.super_ai_orchestrator.integrations.base import Connector
from modules.super_ai_orchestrator.integrations.sibling import make_sibling_connectors
from modules.super_ai_orchestrator.integrations.toolchain import make_toolchain_connectors


def test_registry_has_all_sibling_and_toolchain_connectors():
    registry = ConnectorRegistry()
    sibling = {c.name for c in make_sibling_connectors()}
    toolchain = {c.name for c in make_toolchain_connectors()}
    assert sibling.issubset(registry.connectors)
    assert toolchain.issubset(registry.connectors)
    assert len(registry.all()) == len(sibling) + len(toolchain)
    assert len(sibling) == 7
    assert len(toolchain) == 16


def test_registry_graceful_unknown_connector():
    registry = ConnectorRegistry()
    result = registry.invoke("does_not_exist")
    assert result["status"] == "unknown"
    assert result["available"] is False


def test_unavailable_connector_degrades():
    connector = Connector(
        name="missing",
        display="Missing",
        tools=("x",),
        available=False,
        note="not installed",
    )
    result = connector.execute("invoke", target="t")
    assert result["status"] == "unavailable"
    assert result["available"] is False
    assert result["note"] == "not installed"


def test_available_connector_without_handler_delegates():
    connector = Connector(name="sibling", display="Sibling", tools=("t",), available=True)
    result = connector.execute("invoke")
    assert result["status"] == "delegated"
    assert result["available"] is True
    assert result["connector"] == "sibling"


def test_connector_handler_result_and_error_wrapping():
    connector = Connector(
        name="good",
        display="Good",
        tools=("t",),
        available=True,
        handler=lambda action, **kwargs: {"status": "ok", "value": kwargs.get("v")},
    )
    result = connector.execute("invoke", v=42)
    assert result == {"status": "ok", "value": 42, "available": True, "connector": "good", "action": "invoke"}

    broken = Connector(
        name="broken",
        display="Broken",
        tools=("t",),
        available=True,
        handler=lambda action, **kwargs: 1 / 0,
    )
    error = broken.execute()
    assert error["status"] == "error"
    assert "error" in error
    assert error["available"] is True


def test_registry_tools_and_by_tool():
    registry = ConnectorRegistry()
    tools = registry.tools()
    assert "git" in tools
    assert "llm" in tools
    assert "knowledge_graph" in tools
    assert registry.by_tool("git")
    assert registry.by_tool("no-such-tool") == ()


def test_registry_register_custom_connector():
    registry = ConnectorRegistry()
    custom = Connector(
        name="custom_thing",
        display="Custom",
        tools=("custom",),
        available=True,
        handler=lambda action, **kwargs: {"status": "ok"},
    )
    registry.register(custom)
    assert registry.get("custom_thing") is custom
    result = registry.invoke("custom_thing")
    assert result["status"] == "ok"


def test_connector_info_serialization():
    connector = Connector(name="c", display="C", tools=("t",), available=True)
    data = connector.to_dict()
    assert data["name"] == "c"
    assert data["tools"] == ["t"]
    assert data["available"] is True
