from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class AIManager:
    """Manages all AI sub-modules and their lifecycle."""

    def __init__(self):
        self._modules: dict[str, Any] = {}
        self._module_types: dict[str, str] = {}

    def register_module(self, name: str, module: Any, module_type: str | None = None) -> None:
        """Register a sub-module by name."""
        self._modules[name] = module
        self._module_types[name] = module_type or type(module).__name__

    def unregister_module(self, name: str) -> None:
        """Unregister a sub-module."""
        self._modules.pop(name, None)
        self._module_types.pop(name, None)

    def get_module(self, name: str) -> Any | None:
        """Get a registered module by name."""
        return self._modules.get(name)

    def list_modules(self) -> dict[str, str]:
        """List all registered modules with their types."""
        return dict(self._module_types)

    def health(self) -> dict[str, Any]:
        """Get health status of all registered modules."""
        statuses: dict[str, Any] = {}
        for name, module in self._modules.items():
            if hasattr(module, "health"):
                try:
                    statuses[name] = module.health()
                except Exception as e:
                    statuses[name] = {"status": "error", "error": str(e)}
            else:
                statuses[name] = {"status": "unknown", "type": type(module).__name__}
        return {
            "module_count": len(self._modules),
            "modules": statuses,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def __contains__(self, name: str) -> bool:
        return name in self._modules

    def __len__(self) -> int:
        return len(self._modules)

    def __repr__(self) -> str:
        modules = ", ".join(self._modules.keys())
        return f"AIManager({modules})"
