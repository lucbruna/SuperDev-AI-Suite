from __future__ import annotations

from typing import Any

DEFAULT_TEMPLATES: dict[str, dict[str, Any]] = {
    "microservices": {
        "name": "microservices",
        "description": "Decompose into independently deployable services",
        "components": [
            {"name": "APIGateway", "responsibility": "Request routing and auth"},
            {"name": "ServiceRegistry", "responsibility": "Service discovery"},
            {"name": "ConfigServer", "responsibility": "External configuration"},
        ],
        "patterns": ["microservices", "event_driven"],
        "layers": ["gateway", "service", "data"],
    },
    "monolith": {
        "name": "monolith",
        "description": "Single deployable application with modular structure",
        "components": [
            {"name": "WebLayer", "responsibility": "HTTP handling and views"},
            {"name": "BusinessLayer", "responsibility": "Core business logic"},
            {"name": "DataLayer", "responsibility": "Data access and persistence"},
        ],
        "patterns": ["layered"],
        "layers": ["presentation", "business", "data"],
    },
    "layered": {
        "name": "layered",
        "description": "Horizontal layers with strict dependency direction",
        "components": [
            {"name": "Presentation", "responsibility": "User interface"},
            {"name": "Application", "responsibility": "Use case orchestration"},
            {"name": "Domain", "responsibility": "Business rules"},
            {"name": "Infrastructure", "responsibility": "Technical capabilities"},
        ],
        "patterns": ["layered"],
        "layers": ["presentation", "application", "domain", "infrastructure"],
    },
    "event_driven": {
        "name": "event_driven",
        "description": "Asynchronous event-based communication",
        "components": [
            {"name": "EventBus", "responsibility": "Event routing and delivery"},
            {"name": "EventStore", "responsibility": "Event persistence"},
            {"name": "EventProcessor", "responsibility": "Event handling logic"},
        ],
        "patterns": ["event_driven", "message_queue"],
        "layers": ["producer", "bus", "consumer"],
    },
}


class TemplateManager:
    """Manages architecture templates and blueprints for common patterns."""

    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {k: dict(v) for k, v in DEFAULT_TEMPLATES.items()}

    def get_template(self, name: str) -> dict[str, Any] | None:
        template = self._templates.get(name)
        if template:
            return dict(template)
        return None

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())

    def add_template(self, name: str, template: dict[str, Any]) -> str:
        self._templates[name] = {**template, "name": name}
        return name

    def apply_template(
        self,
        name: str,
        customization: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        template = self._templates.get(name)
        if template is None:
            return {"error": f"Template '{name}' not found"}
        result: dict[str, Any] = {
            k: list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v for k, v in template.items()
        }
        if customization:
            components: list[Any] = list(result.get("components", []))
            extra_components: list[Any] = list(customization.get("components", []))
            components.extend(extra_components)
            result["components"] = components
            for key, value in customization.items():
                if key not in ("components",) and key in result:
                    result[key] = value
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "templates": list(self._templates.values()),
            "template_count": len(self._templates),
        }
