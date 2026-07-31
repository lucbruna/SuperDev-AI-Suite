"""
Integration Factory - Create integration instances
"""
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FactoryType(Enum):
    REST = "rest"
    SOAP = "soap"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    DATABASE = "database"
    FILE = "file"
    WEBHOOK = "webhook"
    MESSAGE_QUEUE = "message_queue"
    CUSTOM = "custom"


@dataclass
class FactoryTemplate:
    template_id: str
    name: str
    factory_type: FactoryType
    default_config: dict[str, Any] = field(default_factory=dict)
    description: str = ""


class IntegrationFactory:
    def __init__(self):
        self.templates: dict[str, FactoryTemplate] = {}
        self.created_count: dict[str, int] = {}
        self._setup_defaults()

    def _setup_defaults(self):
        defaults = {
            FactoryType.REST: {"method": "GET", "timeout": 30, "retries": 3, "headers": {"Content-Type": "application/json"}},
            FactoryType.SOAP: {"version": "1.2", "timeout": 60},
            FactoryType.GRAPHQL: {"timeout": 30, "batch": False},
            FactoryType.DATABASE: {"pool_size": 5, "timeout": 30},
            FactoryType.FILE: {"encoding": "utf-8", "mode": "r"},
            FactoryType.WEBHOOK: {"method": "POST", "timeout": 10, "retries": 3},
            FactoryType.MESSAGE_QUEUE: {"queue_size": 1000, "workers": 4},
        }
        for ftype, config in defaults.items():
            template_id = hashlib.sha256(ftype.value.encode()).hexdigest()[:16]
            self.templates[template_id] = FactoryTemplate(template_id=template_id, name=f"{ftype.value}_template", factory_type=ftype, default_config=config)

    def register_template(self, name: str, factory_type: FactoryType, default_config: dict[str, Any] = None) -> FactoryTemplate:
        template_id = hashlib.sha256(f"{name}{factory_type.value}".encode()).hexdigest()[:16]
        template = FactoryTemplate(template_id=template_id, name=name, factory_type=factory_type, default_config=default_config or {})
        self.templates[template_id] = template
        return template

    def create(self, factory_type: FactoryType, config: dict[str, Any] = None) -> dict[str, Any]:
        template = self._find_template(factory_type)
        merged_config = {**(template.default_config if template else {}), **(config or {})}
        instance_id = hashlib.sha256(f"{factory_type.value}{str(merged_config)}".encode()).hexdigest()[:16]
        self.created_count[factory_type.value] = self.created_count.get(factory_type.value, 0) + 1
        return {"instance_id": instance_id, "factory_type": factory_type.value, "config": merged_config}

    def _find_template(self, factory_type: FactoryType) -> FactoryTemplate | None:
        for template in self.templates.values():
            if template.factory_type == factory_type:
                return template
        return None

    def get_template(self, template_id: str) -> FactoryTemplate | None:
        return self.templates.get(template_id)

    def list_templates(self) -> list:
        return list(self.templates.values())

    def get_created_count(self) -> dict[str, int]:
        return self.created_count.copy()

    def count(self) -> int:
        return len(self.templates)
