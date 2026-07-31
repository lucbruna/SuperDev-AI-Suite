"""Designer for creating and modifying architectures."""

from typing import Any

from .models import (
    ArchitectureComponent,
    ComponentType,
    Connector,
    ConnectorType,
    PatternType,
)


class ArchitectureDesigner:
    """Creates and modifies architecture designs."""

    def __init__(self):
        self._templates: dict[str, dict[str, Any]] = {}

    def create_component(
        self, name: str, component_type: ComponentType, technology: str = "", **kwargs
    ) -> ArchitectureComponent:
        return ArchitectureComponent(
            name=name,
            component_type=component_type,
            technology=technology,
            **kwargs,
        )

    def create_connector(
        self, source_id: str, target_id: str, connector_type: ConnectorType = ConnectorType.SYNCHRONOUS, **kwargs
    ) -> Connector:
        return Connector(
            source_id=source_id,
            target_id=target_id,
            connector_type=connector_type,
            **kwargs,
        )

    def apply_pattern(self, pattern_type: PatternType) -> dict[str, Any]:
        """Apply a known architectural pattern."""
        patterns = {
            PatternType.MICROSERVICES: {
                "components": ["api_gateway", "service_registry", "config_server", "service_a", "service_b"],
                "connectors": [("api_gateway", "service_a", "http"), ("api_gateway", "service_b", "http")],
                "trade_offs": {"scalability": "high", "complexity": "high", "latency": "medium"},
            },
            PatternType.EVENT_DRIVEN: {
                "components": ["event_producer", "event_broker", "event_consumer"],
                "connectors": [
                    ("event_producer", "event_broker", "async"),
                    ("event_broker", "event_consumer", "async"),
                ],
                "trade_offs": {"loose_coupling": "high", "debugging": "hard", "throughput": "high"},
            },
            PatternType.LAYERED: {
                "components": ["presentation", "business", "data_access", "database"],
                "connectors": [("presentation", "business", "sync"), ("business", "data_access", "sync")],
                "trade_offs": {"separation": "high", "performance": "medium", "simplicity": "high"},
            },
            PatternType.CQRS: {
                "components": ["command_handler", "query_handler", "command_store", "query_store", "event_bus"],
                "connectors": [],
                "trade_offs": {"read_performance": "high", "consistency": "eventual", "complexity": "high"},
            },
        }
        return patterns.get(pattern_type, {"components": [], "connectors": [], "trade_offs": {}})

    def register_template(self, name: str, template: dict[str, Any]) -> None:
        self._templates[name] = template

    def get_template(self, name: str) -> dict[str, Any] | None:
        return self._templates.get(name)

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())
