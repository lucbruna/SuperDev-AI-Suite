"""Lifecycle manager for the Digital Twin module.

Owns the runtime wiring (config, context, engine, kernel), provides the
public operations the CLI/API call, and guards against conflicting states.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config.constants import TWIN_SYNCED, TWIN_OUT_OF_SYNC
from modules.digital_twin.config.digital_twin_config import DigitalTwinConfig
from modules.digital_twin.core.digital_twin_context import DigitalTwinContext
from modules.digital_twin.core.digital_twin_engine import DigitalTwinEngine, EngineResult
from modules.digital_twin.core.digital_twin_kernel import DigitalTwinKernel
from modules.digital_twin.core.digital_twin_registry import TwinRegistry


@dataclass(slots=True)
class ManagerState:
    """Public state snapshot reported by the manager."""

    running: bool
    cycles: int
    twin_status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "running": self.running,
            "cycles": self.cycles,
            "twin_status": self.twin_status,
        }


class DigitalTwinManager:
    """High-level operations for a Digital Twin instance."""

    def __init__(
        self,
        config: DigitalTwinConfig | None = None,
        registry: TwinRegistry | None = None,
        context: DigitalTwinContext | None = None,
        engine: DigitalTwinEngine | None = None,
        kernel: DigitalTwinKernel | None = None,
    ) -> None:
        self._config = config or DigitalTwinConfig()
        self._ctx = context or DigitalTwinContext(
            config=self._config,
            registry=registry or TwinRegistry(),
        )
        self._engine = engine or DigitalTwinEngine()
        self._kernel = kernel or DigitalTwinKernel(self._ctx, self._engine)

    @property
    def context(self) -> DigitalTwinContext:
        return self._ctx

    def start(self) -> None:
        self._kernel.start()
        self._ctx.state.set_twin_status(TWIN_OUT_OF_SYNC)
        self._ctx.publish("twin.started", {"config_name": self._config.name})

    def stop(self) -> None:
        self._kernel.stop()
        self._ctx.publish("twin.stopped", {})

    def run_cycle(self) -> EngineResult:
        result = self._engine.run(self._ctx)
        self._ctx.state.set_twin_status(TWIN_SYNCED)
        return result

    def tick(self, steps: int = 1) -> int:
        return self._kernel.tick(steps)

    def register_component(self, name: str, component, *, overwrite: bool = False) -> None:
        self._ctx.registry.register(name, component, overwrite=overwrite)

    def state(self) -> ManagerState:
        return ManagerState(
            running=self._kernel.status().running,
            cycles=self._engine.cycles,
            twin_status=self._ctx.state.twin_status,
        )
