from __future__ import annotations

import logging
from typing import Any, Callable

from ..integration_interfaces import Connector
from ..integration_models import ConnectionConfig


class BaseConnector(Connector):
    """Base connector with connection state management and an operation table.

    Providers subclass this and register operations via `register_operation`
    or by defining `_operations`.
    """

    connector_type: str = "generic"
    display_name: str = "Generic Connector"
    version: str = "1.0.0"

    def __init__(self) -> None:
        self._log = logging.getLogger(f"superdev.integration.connectors.{self.connector_type}")
        self._connected = False
        self._config: ConnectionConfig | None = None
        self._operations: dict[str, Callable[..., Any]] = {}

    # --- Connector ABC -----------------------------------------------------

    def connect(self, config: ConnectionConfig) -> bool:
        self._config = config
        try:
            self._connected = self._do_connect(config)
        except Exception as exc:  # noqa: BLE001
            self._log.warning("connect failed: %s", exc)
            self._connected = False
        return self._connected

    def disconnect(self) -> bool:
        try:
            self._do_disconnect()
        except Exception as exc:  # noqa: BLE001
            self._log.warning("disconnect failed: %s", exc)
        self._connected = False
        return True

    def invoke(self, operation: str, params: dict[str, Any] | None = None) -> Any:
        handler = self._operations.get(operation)
        if handler is None:
            raise KeyError(f"connector {self.connector_type!r} has no operation {operation!r}")
        return handler(params or {})

    def test(self) -> bool:
        try:
            return self._do_test()
        except Exception as exc:  # noqa: BLE001
            self._log.warning("test failed: %s", exc)
            return False

    def status(self) -> str:
        return "connected" if self._connected else "disconnected"

    def is_connected(self) -> bool:
        return self._connected

    def operations(self) -> list[str]:
        return sorted(self._operations)

    # --- Registration --------------------------------------------------------

    def register_operation(self, name: str, handler: Callable[..., Any]) -> None:
        self._operations[name] = handler

    def register_many(self, handlers: dict[str, Callable[..., Any]]) -> None:
        self._operations.update(handlers)

    # --- Hooks for subclasses --------------------------------------------------

    def _do_connect(self, config: ConnectionConfig) -> bool:
        return True

    def _do_disconnect(self) -> None:
        pass

    def _do_test(self) -> bool:
        return True


class GenericConnector(BaseConnector):
    """Default connector used when no provider is registered for a type."""

    connector_type = "generic"
    display_name = "Generic Connector"

    def __init__(self, connector_type: str = "generic") -> None:
        super().__init__()
        self.connector_type = connector_type
        self.display_name = f"{connector_type} connector"
        self.register_operation("ping", lambda params: {"pong": True})

    def _do_test(self) -> bool:
        return True


class ProviderConnector(BaseConnector):
    """Base for library providers: holds an in-memory record store so provider
    operations (list/get/create/update/delete) behave realistically offline.
    """

    def __init__(self) -> None:
        super().__init__()
        self._records: list[dict[str, Any]] = []
        self._next_id = 1

    # --- record store helpers ------------------------------------------------

    def _add(self, record: dict[str, Any]) -> dict[str, Any]:
        record = dict(record)
        record.setdefault("id", str(self._next_id))
        self._next_id += 1
        self._records.append(record)
        return record

    def _all(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        records = self._records
        if filters:
            records = [r for r in records if all(r.get(k) == v for k, v in filters.items())]
        return [dict(r) for r in records]

    def _find(self, record_id: str) -> dict[str, Any] | None:
        for record in self._records:
            if str(record.get("id")) == str(record_id):
                return record
        return None

    def _update(self, record_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        record = self._find(record_id)
        if record is None:
            return None
        record.update(changes)
        return dict(record)

    def _delete(self, record_id: str) -> bool:
        before = len(self._records)
        self._records = [r for r in self._records if str(r.get("id")) != str(record_id)]
        return len(self._records) < before

    def _require_connected(self) -> None:
        if not self.is_connected():
            raise RuntimeError(f"connector {self.connector_type!r} is not connected")
