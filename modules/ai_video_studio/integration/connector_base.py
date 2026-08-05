"""Domain connector base — contract shared by every Volume 10 connector.

Each business connector (Enterprise AI, Agriculture, ERP, CRM, HR,
Finance, BI, Security, Automation, Notifications, Knowledge, Cloud,
Monitoring, Supervisor, Gateway, Message Bus, Learning) implements the
same surface: ``connect()`` / ``status()`` / ``capabilities()`` /
``execute(action, data)``. Actions are registered with ``_register`` and
never raise — every result is a JSON-serializable dict.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable

from modules.ai_video_studio.integration.event_bus import get_event_bus


class DomainConnector:
    """Base connector: action registry + lifecycle + safe execution."""

    domain: str = "generic"
    description: str = ""

    def __init__(self) -> None:
        self._connected = False
        self._last_error: str | None = None
        self._ops: dict[str, Callable[[dict[str, Any]], Any]] = {}

    # ── action registry ──────────────────────────────────────────
    def _register(self, name: str, fn: Callable[[dict[str, Any]], Any]) -> None:
        """Register ``fn(data: dict) -> dict`` under ``name``."""
        self._ops[name] = fn

    # ── lifecycle ────────────────────────────────────────────────
    def connect(self) -> dict[str, Any]:
        """Mark the connector connected and return its status."""
        self._connected = True
        return self.status()

    def disconnect(self) -> dict[str, Any]:
        self._connected = False
        return self.status()

    # ── introspection ────────────────────────────────────────────
    def actions(self) -> list[str]:
        return sorted(self._ops)

    def status(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "connected": self._connected,
            "description": self.description,
            "actions": self.actions(),
            "error": self._last_error,
        }

    def capabilities(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "description": self.description,
            "actions": self.actions(),
        }

    # ── execution ────────────────────────────────────────────────
    def execute(self, action: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run an action safely; returns ``{ok, ...}`` or ``{ok: False, error}``."""
        handler = self._ops.get(action)
        if handler is None:
            return {"ok": False, "error": f"unknown action '{action}' (available: {self.actions()})"}
        try:
            result = handler(dict(data or {}))
            if isinstance(result, dict) and "ok" not in result:
                result = {"ok": True, **result}
            return result
        except Exception as e:  # noqa: BLE001 — connectors must never raise
            self._last_error = str(e)
            return {"ok": False, "error": str(e)}

    # ── helpers ──────────────────────────────────────────────────
    @staticmethod
    def publish_sync(event_type: str, **payload: Any) -> None:
        """Fire-and-forget publish to the studio event bus (never raises)."""
        try:
            asyncio.get_event_loop().run_until_complete(
                get_event_bus().publish(event_type, **payload)
            )
        except RuntimeError:
            pass

    @staticmethod
    def _require(data: dict[str, Any], *keys: str, action: str) -> dict[str, Any] | None:
        """Return an error dict when any key is missing, else None."""
        missing = [k for k in keys if not data.get(k)]
        if missing:
            return {"ok": False, "error": f"{action}: missing required field(s): {', '.join(missing)}"}
        return None
