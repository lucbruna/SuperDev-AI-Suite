"""ModuleLoader: executes module entrypoints and drives lifecycle transitions."""
from __future__ import annotations

from typing import Any

from aios.module_registry.module import Module
from aios.module_registry.module_lifecycle import ModuleLifecycle


class ModuleLoader:
    def __init__(self, lifecycle: ModuleLifecycle | None = None) -> None:
        self.lifecycle = lifecycle if lifecycle is not None else ModuleLifecycle()

    def load(self, module: Module) -> bool:
        self.lifecycle.set_state(module.module_id, "loading")
        try:
            if callable(module.entrypoint):
                module.metadata["load_result"] = module.entrypoint()
            module.status = "active"
            self.lifecycle.set_state(module.module_id, "active")
            return True
        except Exception as exc:
            module.status = "failed"
            module.metadata["load_error"] = str(exc)
            self.lifecycle.set_state(module.module_id, "failed")
            return False

    def unload(self, module: Module) -> bool:
        self.lifecycle.set_state(module.module_id, "unloaded")
        module.status = "unloaded"
        return True

    def stats(self) -> dict[str, Any]:
        events = self.lifecycle.events()
        return {
            "load_attempts": sum(1 for e in events if e["to"] == "loading"),
            "load_ok": sum(1 for e in events if e["to"] == "active" and e["ok"]),
            "load_failed": sum(1 for e in events if e["to"] == "failed" and e["ok"]),
        }
