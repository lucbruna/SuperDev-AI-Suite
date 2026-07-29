"""State Manager — persistent global state for the SuperDev platform.

Stores and retrieves system state, session data, runtime configuration
overrides, and recovery checkpoints with optional file-based persistence.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class StateManager:
    """Manages global system state with optional persistence.

    The state manager stores:
    - Runtime configuration overrides
    - System metadata (boot time, version, environment)
    - Recovery checkpoints for crash recovery
    - Arbitrary key-value state shared across modules
    """

    def __init__(self, persist_path: str = "") -> None:
        self._state: dict[str, Any] = {}
        self._persist_path = persist_path
        self._changed_keys: set[str] = set()

    # ─── Core State ───────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Initialize state from persistence file if available."""
        if self._persist_path:
            try:
                with open(self._persist_path) as f:
                    data = json.load(f)
                self._state.update(data)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        self._state.setdefault("system", {
            "boot_count": 0,
            "last_boot": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    async def set(self, key: str, value: Any) -> None:
        """Set a state value."""
        self._state[key] = value
        self._changed_keys.add(key)

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self._state.get(key, default)

    async def delete(self, key: str) -> bool:
        """Delete a state key. Returns True if it existed."""
        if key in self._state:
            del self._state[key]
            self._changed_keys.add(key)
            return True
        return False

    async def get_all(self) -> dict[str, Any]:
        """Get a copy of the entire state."""
        return dict(self._state)

    # ─── Namespaced State ─────────────────────────────────────────────────

    async def ns_set(self, namespace: str, key: str, value: Any) -> None:
        """Set a value within a namespace."""
        ns = self._state.setdefault(f"ns:{namespace}", {})
        ns[key] = value
        self._changed_keys.add(f"ns:{namespace}")

    async def ns_get(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get a value within a namespace."""
        ns = self._state.get(f"ns:{namespace}", {})
        return ns.get(key, default)

    async def ns_list(self, namespace: str) -> dict[str, Any]:
        """Get all key-value pairs within a namespace."""
        return dict(self._state.get(f"ns:{namespace}", {}))

    # ─── System Metadata ──────────────────────────────────────────────────

    async def record_boot(self) -> int:
        """Record a system boot event. Returns the boot count."""
        system = self._state.setdefault("system", {})
        boot_count = system.get("boot_count", 0) + 1
        system["boot_count"] = boot_count
        system["last_boot"] = datetime.now(timezone.utc).isoformat()
        self._changed_keys.add("system")
        return boot_count

    async def get_boot_count(self) -> int:
        """Get the total number of system boots."""
        system = self._state.get("system", {})
        return system.get("boot_count", 0)

    async def set_metadata(self, **kwargs: Any) -> None:
        """Set system metadata fields."""
        meta = self._state.setdefault("metadata", {})
        meta.update(kwargs)
        self._changed_keys.add("metadata")

    async def get_metadata(self) -> dict[str, Any]:
        """Get system metadata."""
        return dict(self._state.get("metadata", {}))

    # ─── Recovery Checkpoints ─────────────────────────────────────────────

    async def save_checkpoint(self, name: str, data: dict[str, Any]) -> None:
        """Save a recovery checkpoint."""
        checkpoints = self._state.setdefault("checkpoints", {})
        checkpoints[name] = {
            "data": data,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        self._changed_keys.add("checkpoints")

    async def load_checkpoint(self, name: str) -> dict[str, Any] | None:
        """Load a recovery checkpoint."""
        checkpoints = self._state.get("checkpoints", {})
        cp = checkpoints.get(name)
        return cp.get("data") if cp else None

    async def list_checkpoints(self) -> list[dict[str, Any]]:
        """List all saved checkpoints."""
        checkpoints = self._state.get("checkpoints", {})
        return [
            {"name": name, "saved_at": cp["saved_at"]}
            for name, cp in checkpoints.items()
        ]

    # ─── Persistence ──────────────────────────────────────────────────────

    async def persist(self) -> bool:
        """Persist state to file. Returns True on success."""
        if not self._persist_path:
            return False
        try:
            with open(self._persist_path, "w") as f:
                json.dump(self._state, f, indent=2, default=str)
            self._changed_keys.clear()
            return True
        except Exception:
            return False

    async def persist_if_changed(self) -> bool:
        """Persist only if state has changed since last persist."""
        if self._changed_keys:
            return await self.persist()
        return False

    # ─── Statistics ───────────────────────────────────────────────────────

    def get_statistics(self) -> dict[str, Any]:
        """Get state manager statistics."""
        return {
            "total_keys": len(self._state),
            "changed_keys": len(self._changed_keys),
            "has_persistence": bool(self._persist_path),
            "sections": [
                k for k in self._state.keys()
                if isinstance(self._state[k], dict)
            ],
        }
