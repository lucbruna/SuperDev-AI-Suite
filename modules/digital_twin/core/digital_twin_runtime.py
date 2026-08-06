"""Top-level runtime facade for the Digital Twin module.

Wires config, context, engine, kernel and manager into one object with a
fresh registry per instance — no shared singleton (AD registry pattern).
"""
from __future__ import annotations

from modules.digital_twin.config.digital_twin_config import DigitalTwinConfig
from modules.digital_twin.core.digital_twin_context import DigitalTwinContext
from modules.digital_twin.core.digital_twin_engine import DigitalTwinEngine, EngineResult
from modules.digital_twin.core.digital_twin_kernel import DigitalTwinKernel, KernelStatus
from modules.digital_twin.core.digital_twin_manager import DigitalTwinManager, ManagerState
from modules.digital_twin.core.digital_twin_registry import TwinRegistry


class DigitalTwinRuntime:
    """Facade combining context, engine, kernel and manager."""

    def __init__(
        self,
        config: DigitalTwinConfig | None = None,
        registry: TwinRegistry | None = None,
    ) -> None:
        self._config = config or DigitalTwinConfig()
        self._registry = registry or TwinRegistry()
        self._ctx = DigitalTwinContext(config=self._config, registry=self._registry)
        self._engine = DigitalTwinEngine()
        self._kernel = DigitalTwinKernel(self._ctx, self._engine)
        self._manager = DigitalTwinManager(
            config=self._config,
            registry=self._registry,
            context=self._ctx,
            engine=self._engine,
            kernel=self._kernel,
        )

    @property
    def config(self) -> DigitalTwinConfig:
        return self._config

    @property
    def context(self) -> DigitalTwinContext:
        return self._ctx

    @property
    def registry(self) -> TwinRegistry:
        return self._registry

    @property
    def engine(self) -> DigitalTwinEngine:
        return self._engine

    @property
    def kernel(self) -> DigitalTwinKernel:
        return self._kernel

    @property
    def manager(self) -> DigitalTwinManager:
        return self._manager

    def start(self) -> None:
        self._manager.start()

    def stop(self) -> None:
        self._manager.stop()

    def run_cycle(self) -> EngineResult:
        return self._manager.run_cycle()

    def tick(self, steps: int = 1) -> int:
        return self._manager.tick(steps)

    def register_component(self, name: str, component, *, overwrite: bool = False) -> None:
        self._manager.register_component(name, component, overwrite=overwrite)

    def kernel_status(self) -> KernelStatus:
        return self._kernel.status()

    def manager_state(self) -> ManagerState:
        return self._manager.state()
