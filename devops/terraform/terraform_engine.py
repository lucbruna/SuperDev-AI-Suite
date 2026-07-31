from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from ..devops_context import DevOpsContext
from ..devops_store import load_json, save_json


class TerraformEngine:
    """Manages Terraform infrastructure-as-code workflows (in-memory)."""

    def __init__(self, context: DevOpsContext | None = None, store_path: str | Path | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.terraform")
        self._context = context
        self._store = Path(store_path) if store_path else None
        self._state: dict[str, dict[str, Any]] = {}
        self._load_state()

    def init(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        """Initialize a Terraform working directory."""
        self._state.setdefault(directory, {"resources": [], "outputs": {}})
        self._persist()
        return {
            "directory": directory,
            "status": "initialized",
            "init_at": time.time(),
            "options": dict(kwargs),
        }

    def plan(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        """Generate an execution plan."""
        changes = kwargs.get("resources") or [f"resource.{name}" for name in (kwargs.get("names") or ["default"])]
        return {
            "directory": directory,
            "status": "planned",
            "plan_id": f"plan-{directory}-{int(time.time())}",
            "resources": list(changes),
            "plan_at": time.time(),
        }

    def apply(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        """Apply the plan, recording resources in the in-memory state."""
        resources = kwargs.get("resources") or []
        state = self._state.setdefault(directory, {"resources": [], "outputs": {}})
        state["resources"] = list(resources) if resources else state["resources"]
        state["updated_at"] = time.time()
        self._persist()
        return {
            "directory": directory,
            "status": "applied",
            "resources": list(state["resources"]),
            "apply_at": time.time(),
        }

    def destroy(self, directory: str, **kwargs: Any) -> dict[str, Any]:
        """Destroy tracked resources for a directory."""
        state = self._state.get(directory)
        destroyed = list(state["resources"]) if state else []
        self._state.pop(directory, None)
        self._persist()
        return {
            "directory": directory,
            "status": "destroyed",
            "destroyed_resources": destroyed,
            "destroy_at": time.time(),
            "options": dict(kwargs),
        }

    def validate(self, directory: str) -> dict[str, Any]:
        return {"directory": directory, "valid": True, "errors": []}

    def fmt(self, directory: str) -> dict[str, Any]:
        return {"directory": directory, "formatted": True}

    def state_list(self, directory: str) -> list[str]:
        state = self._state.get(directory, {})
        return list(state.get("resources", []))

    def state_show(self, directory: str, resource: str) -> dict[str, Any]:
        state = self._state.get(directory, {})
        if resource not in state.get("resources", []):
            raise KeyError(f"resource not found in state: {resource}")
        return {"resource": resource, "directory": directory, "status": "present"}

    def state_rm(self, directory: str, resource: str) -> bool:
        state = self._state.get(directory)
        if state is None or resource not in state.get("resources", []):
            return False
        state["resources"].remove(resource)
        self._persist()
        return True

    def output(self, directory: str, name: str | None = None) -> dict[str, Any]:
        state = self._state.get(directory, {})
        outputs = state.get("outputs", {})
        if name is not None:
            return {"name": name, "value": outputs.get(name)}
        return dict(outputs)

    # -- persistence ---------------------------------------------------------

    def _load_state(self) -> None:
        """Restore the per-directory resource state from ``terraform.json``."""
        if self._store is None:
            return
        data = load_json(self._store / "terraform.json", default={})
        if not isinstance(data, dict):
            return
        state = data.get("state")
        if isinstance(state, dict):
            self._state = state

    def _persist(self) -> None:
        """Atomically write the terraform state to disk."""
        if self._store is None:
            return
        save_json(self._store / "terraform.json", {"state": self._state})

    def save_state(self) -> None:
        """Persist the terraform state (no-op without ``store_path``)."""
        self._persist()

    def reload_state(self) -> None:
        """Reload the terraform state from disk."""
        self._load_state()
