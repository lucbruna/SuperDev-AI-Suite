from __future__ import annotations

import json
import logging
import time
from typing import Any


class DeploymentHistory:
    """Tracks deployment history and audit trail (in-memory)."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.history")
        self._entries: list[dict[str, Any]] = []

    def record(self, deployment_id: str, service: str, version: str, **kwargs: Any) -> dict[str, Any]:
        """Append a deployment entry to the audit trail."""
        entry: dict[str, Any] = {
            "deployment_id": deployment_id,
            "service": service,
            "version": version,
            "timestamp": time.time(),
        }
        entry.update(kwargs)
        self._entries.append(entry)
        return dict(entry)

    def get(self, deployment_id: str) -> dict[str, Any]:
        """Return the most recent entry for a deployment id."""
        for entry in reversed(self._entries):
            if entry["deployment_id"] == deployment_id:
                return dict(entry)
        raise KeyError(f"deployment not found in history: {deployment_id}")

    def list(self, service: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """List history entries, optionally filtered by service."""
        entries = self._entries
        if service is not None:
            entries = [e for e in entries if e["service"] == service]
        return [dict(e) for e in entries[-limit:]]

    def entries(self) -> list[dict[str, Any]]:
        """Return all history entries (for persistence)."""
        return [dict(e) for e in self._entries]

    def load(self, entries: list[dict[str, Any]]) -> None:
        """Restore history from persisted entries."""
        self._entries = [dict(e) for e in entries]

    def diff(self, first: str, second: str) -> dict[str, Any]:
        """Compare two deployment history entries."""
        a, b = self.get(first), self.get(second)
        return {
            "first": a,
            "second": b,
            "version_changed": a.get("version") != b.get("version"),
            "status_changed": a.get("status") != b.get("status"),
            "environment_changed": a.get("environment") != b.get("environment"),
        }

    def export(self) -> str:
        """Export the full audit trail as a JSON string."""
        return json.dumps(self._entries, indent=2, default=str)
