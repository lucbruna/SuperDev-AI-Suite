from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from ..devops_context import DevOpsContext
from ..devops_store import load_json, save_json


class EnvironmentsEngine:
    """Manages development, staging, production environment lifecycle (in-memory)."""

    def __init__(self, context: DevOpsContext | None = None, store_path: str | Path | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.environments")
        self._context = context
        self._store = Path(store_path) if store_path else None
        self._environments: dict[str, dict[str, Any]] = {}
        self._load_state()

    def create(self, name: str, environment_type: str, **kwargs: Any) -> dict[str, Any]:
        """Create an environment."""
        if name in self._environments:
            raise ValueError(f"environment already exists: {name}")
        record: dict[str, Any] = {
            "name": name,
            "environment_type": environment_type,
            "status": "created",
            "active": False,
            "created_at": time.time(),
            "variables": dict(kwargs.get("variables", {})),
        }
        record.update({k: v for k, v in kwargs.items() if k != "variables"})
        self._environments[name] = record
        self._persist()
        return dict(record)

    def destroy(self, name: str) -> bool:
        """Destroy an environment. Returns False when it doesn't exist."""
        removed = self._environments.pop(name, None) is not None
        if removed:
            self._persist()
        return removed

    def activate(self, name: str) -> bool:
        record = self._environments.get(name)
        if record is None:
            return False
        record["active"] = True
        record["status"] = "active"
        self._persist()
        return True

    def deactivate(self, name: str) -> bool:
        record = self._environments.get(name)
        if record is None:
            return False
        record["active"] = False
        record["status"] = "inactive"
        self._persist()
        return True

    def list(self) -> list[dict[str, Any]]:
        return [dict(e) for e in self._environments.values()]

    def get(self, name: str) -> dict[str, Any]:
        record = self._environments.get(name)
        if record is None:
            raise KeyError(f"environment not found: {name}")
        return dict(record)

    def variables(self, name: str) -> dict[str, Any]:
        record = self._environments.get(name)
        if record is None:
            raise KeyError(f"environment not found: {name}")
        return dict(record.get("variables", {}))

    def set_variable(self, name: str, key: str, value: Any) -> bool:
        record = self._environments.get(name)
        if record is None:
            return False
        record.setdefault("variables", {})[key] = value
        self._persist()
        return True

    def promote(self, source: str, target: str) -> dict[str, Any]:
        """Promote a source environment to a target (variables carry over)."""
        src = self._environments.get(source)
        if src is None:
            raise KeyError(f"environment not found: {source}")
        record = self._environments.get(target)
        if record is None:
            record = self.create(target, src.get("environment_type", "staging"))
        record.setdefault("variables", {}).update(dict(src.get("variables", {})))
        record["status"] = "promoted"
        record["promoted_from"] = source
        record["promoted_at"] = time.time()
        self._persist()
        return dict(record)

    def status(self, name: str) -> dict[str, Any]:
        record = self._environments.get(name)
        if record is None:
            raise KeyError(f"environment not found: {name}")
        return dict(record)

    # -- persistence ---------------------------------------------------------

    def _load_state(self) -> None:
        """Restore the environment lifecycle records from ``environments_lifecycle.json``."""
        if self._store is None:
            return
        data = load_json(self._store / "environments_lifecycle.json", default={})
        if isinstance(data, dict):
            self._environments = data

    def _persist(self) -> None:
        """Atomically write the environment lifecycle state to disk."""
        if self._store is None:
            return
        save_json(self._store / "environments_lifecycle.json", self._environments)

    def save_state(self) -> None:
        """Persist the environment lifecycle state (no-op without ``store_path``)."""
        self._persist()

    def reload_state(self) -> None:
        """Reload the environment lifecycle state from disk."""
        self._load_state()
