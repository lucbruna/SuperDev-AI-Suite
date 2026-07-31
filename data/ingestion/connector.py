from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..data_models import DataSourceType


class BaseConnector(ABC):
    """Abstract connector for external systems.

    Connectors establish a connection, read rows and disconnect. They are
    the transport layer used by the ingestion subsystem to pull data from
    APIs, databases, files and other sources.
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        self.name = name
        self.config = config or {}
        self.connected = False
        self._last_read_at: float | None = None

    @abstractmethod
    async def connect(self) -> bool:
        """Establish the connection. Returns True on success."""

    @abstractmethod
    async def read(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Read rows of data, optionally filtered by a query."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection and release resources."""

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.API

    def get_status(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": type(self).__name__,
            "source_type": self.get_source_type().value,
            "connected": self.connected,
            "last_read_at": self._last_read_at,
        }


class ConnectorManager:
    """Registry and lifecycle manager for connectors."""

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._connectors: dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector) -> BaseConnector:
        self._connectors[connector.name] = connector
        if self.engine is not None:
            self.engine.registry.register_connector(connector.name, connector)
        return connector

    def unregister(self, name: str) -> bool:
        return self._connectors.pop(name, None) is not None

    def get(self, name: str) -> BaseConnector | None:
        return self._connectors.get(name)

    def list(self) -> list[BaseConnector]:
        return list(self._connectors.values())

    def names(self) -> list[str]:
        return list(self._connectors.keys())

    async def connect_all(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for name, connector in self._connectors.items():
            try:
                results[name] = await connector.connect()
            except Exception:
                results[name] = False
        return results

    async def disconnect_all(self) -> None:
        for connector in self._connectors.values():
            try:
                await connector.disconnect()
            except Exception:
                pass

    def status(self) -> dict[str, Any]:
        return {
            "connectors": {
                name: connector.get_status()
                for name, connector in self._connectors.items()
            },
            "count": len(self._connectors),
        }


__all__ = ["BaseConnector", "ConnectorManager"]
