"""Controllers: API-facing operations over the twin manager."""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.api.digital_twin_responses import ApiResponse
from modules.digital_twin.api.digital_twin_serializers import TwinSerializers
from modules.digital_twin.core.digital_twin_manager import DigitalTwinManager
from modules.digital_twin.twin_engine.digital_twin_analyzer import TwinAnalyzer
from modules.digital_twin.twin_engine.digital_twin_engine import TwinEngine
from modules.digital_twin.twin_engine.digital_twin_registry import TwinModelRegistry
from modules.digital_twin.twin_engine.digital_twin_validator import TwinValidator


@dataclass(slots=True)
class TwinControllers:
    """Thin controller layer between routes and core/manager."""

    manager: DigitalTwinManager
    twin_engine: TwinEngine | None = None
    validator: TwinValidator | None = None
    analyzer: TwinAnalyzer | None = None
    twin_registry: TwinModelRegistry | None = None

    def status(self) -> ApiResponse:
        state = self.manager.state()
        return ApiResponse.success(TwinSerializers.manager_state(state))

    def config(self) -> ApiResponse:
        return ApiResponse.success(TwinSerializers.config(self.manager.context.config))

    def start(self) -> ApiResponse:
        self.manager.start()
        return ApiResponse.success({"running": self.manager.state().running})

    def stop(self) -> ApiResponse:
        self.manager.stop()
        return ApiResponse.success({"running": self.manager.state().running})

    def cycle(self) -> ApiResponse:
        result = self.manager.run_cycle()
        return ApiResponse.success(TwinSerializers.engine_result(result))

    def tick(self, steps: int = 1) -> ApiResponse:
        ran = self.manager.tick(steps)
        return ApiResponse.success({"steps": steps, "cycles_ran": ran})

    def register_component(self, name: str, component) -> ApiResponse:
        self.manager.register_component(name, component, overwrite=True)
        return ApiResponse.success({"component": name, "registered": True})

    def _engine(self) -> TwinEngine:
        return self.twin_engine if self.twin_engine is not None else TwinEngine()

    def _registry(self) -> TwinModelRegistry:
        # NOTE: never use `self.twin_registry or TwinModelRegistry()` here —
        # TwinModelRegistry defines __len__, so an empty registry is falsy and
        # the `or` would silently create a fresh (discarded) registry.
        return (
            self.twin_registry
            if self.twin_registry is not None
            else TwinModelRegistry()
        )

    def build_twin(
        self,
        *,
        name: str = "default",
        raw_entities: list[dict[str, object]] | None = None,
        relationships: list[tuple[str, str, str]] | None = None,
    ) -> ApiResponse:
        result = self._engine().build(
            self.manager.context,
            name=name,
            raw_entities=raw_entities or [],
            relationships=relationships or [],
        )
        registry = self._registry()
        registry.register(result.model, overwrite=True)
        return ApiResponse.success(result.to_dict())

    def snapshot(self, name: str = "default") -> ApiResponse:
        registry = self._registry()
        if not registry.has(name):
            return ApiResponse.failure(f"twin not found: {name}", status_code=404)
        snapshot = registry.snapshot(name)
        return ApiResponse.success(snapshot.to_dict())

    def analyze(self, name: str = "default") -> ApiResponse:
        registry = self._registry()
        if not registry.has(name):
            return ApiResponse.failure(f"twin not found: {name}", status_code=404)
        analyzer = self.analyzer if self.analyzer is not None else TwinAnalyzer()
        analysis = analyzer.analyze(registry.get(name))
        return ApiResponse.success(analysis.to_dict())

    def validate(self, name: str = "default") -> ApiResponse:
        registry = self._registry()
        if not registry.has(name):
            return ApiResponse.failure(f"twin not found: {name}", status_code=404)
        validator = self.validator if self.validator is not None else TwinValidator()
        report = validator.validate(registry.get(name))
        return ApiResponse.success(report.to_dict())
