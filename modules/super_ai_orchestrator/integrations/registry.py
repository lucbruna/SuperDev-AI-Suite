"""ConnectorRegistry — unified access to all connectors."""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.integrations.base import Connector, ConnectorInfo
from modules.super_ai_orchestrator.integrations.sibling import make_sibling_connectors
from modules.super_ai_orchestrator.integrations.toolchain import make_toolchain_connectors


class ConnectorRegistry:
    """Registry of sibling-module and toolchain connectors.

    Attributes:
        connectors: name -> Connector.
    """

    def __init__(self) -> None:
        self.connectors: dict[str, Connector] = {}
        for connector in (*make_sibling_connectors(), *make_toolchain_connectors()):
            self.connectors[connector.name] = connector

    def register(self, connector: Connector) -> None:
        """Register a custom connector (replacing any same-name one)."""
        self.connectors[connector.name] = connector

    def get(self, name: str) -> Connector | None:
        return self.connectors.get(name)

    def all(self) -> tuple[Connector, ...]:
        return tuple(self.connectors.values())

    def available(self) -> tuple[Connector, ...]:
        return tuple(c for c in self.connectors.values() if c.available)

    def unavailable(self) -> tuple[Connector, ...]:
        return tuple(c for c in self.connectors.values() if not c.available)

    def tools(self) -> tuple[str, ...]:
        """All tool names offered by available connectors, sorted."""
        seen: set[str] = set()
        for connector in self.available():
            seen.update(connector.tools)
        return tuple(sorted(seen))

    def by_tool(self, tool: str) -> tuple[Connector, ...]:
        """Connectors (available) that provide the given tool."""
        return tuple(
            c for c in self.available() if tool in c.tools
        )

    def invoke(self, name: str, action: str = "invoke", **kwargs: Any) -> dict[str, Any]:
        """Invoke a connector action; unknown/unavailable degrade gracefully."""
        connector = self.get(name)
        if connector is None:
            return {
                "available": False,
                "connector": name,
                "action": action,
                "status": "unknown",
                "note": "no such connector",
            }
        return connector.execute(action, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "connectors": [c.to_dict() for c in self.all()],
            "available": [c.name for c in self.available()],
        }
